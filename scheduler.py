import random
import numpy
import matplotlib.pyplot as plt

avg_solution_time1 = (0.0020012855529785156 + 0.052039384841918945)/2
avg_solution_time2 = (0.02399897575378418 + 0.16211581230163574)/2
first_range = (0.0020012855529785156, 0.052039384841918945)
second_range = (0.02399897575378418, 0.16211581230163574)
counter = 0

class Task:
    def __init__(self, t, s_t, d):
        self.time = t
        self.solution_time = s_t
        self.deadline = d

def GenerateQueue(periods, solution_time, range_random, tact_size):
    queue = []
    for i in range(len(periods)):
        tasks_per_tact = []
        for j in range(periods[i]):
            error = random.uniform(range_random[0], range_random[1])/2
            if random.random() < 0.5:
                tasks_per_tact.append(Task(i * tact_size, solution_time + error, i * tact_size + (solution_time + error) * random.randint(2,10)))
            else:
                tasks_per_tact.append(Task(i * tact_size, solution_time - error, i * tact_size + (solution_time + error) * random.randint(2,10)))
        queue.append(tasks_per_tact)
    return queue

def SMO(queue, tact_size, number_of_tasks, type_smo):
    Statistic = {
    'average_wait_in_system' : 0,
    'solved_tasks' : 0,
    'average_queue_length' : [],
    'free_time' : 0,
    'skiped_tasks' : []}
    real_time_queue = []
    time = 0
   
    remained_time = 0
    #example number of processors
    n_processors = 4
    in_processor = [0] * n_processors
    

    while True:
        #delete overdue tasks
        empty = true
        for i in in_processor:
            if i != 0:
                empty = false
                break
        
        if empty == true:
            before = len(real_time_queue)
            real_time_queue = [i for i in real_time_queue if i.deadline > time]
            after = len(real_time_queue)
            # print(before, after)
            diff = before - after
            Statistic['skiped_tasks'].append(diff)

        #if all tasks already prepared
        if len(real_time_queue) == 0 and len(queue) == 0:
            print("Finished.")
            break
        #add tasks if it is new tact
        if len(queue) != 0 and remained_time == 0:
            real_time_queue += queue.pop(0)
            Statistic['average_queue_length'].append(len(real_time_queue))

        #if processor is empty - choose the shortest
        empty = true
        for i in in_processor:
            if i != 0:
                empty = false
                break
        
        if in_processor == 0:
            if type_smo == 'RM':
                real_time_queue.sort(key=lambda x: x.solution_time)
            elif type_smo == 'EDF':
                real_time_queue.sort(key=lambda x: x.deadline)

        if len(real_time_queue) != 0:
            #calculate tasks in the same tact
            if remained_time != 0:
                if real_time_queue[0].solution_time > remained_time:
                    time += remained_time
                    real_time_queue[0].solution_time -= remained_time
                    in_processor[counter % n_processors] = 1
                    remained_time = 0
                else:
                    remained_time -= real_time_queue[0].solution_time
                    time += real_time_queue[0].solution_time
                    Statistic['average_wait_in_system'] += time - real_time_queue[0].time - real_time_queue[0].solution_time
                    Statistic['solved_tasks'] += 1
                    del real_time_queue[0]
                    in_processor[counter % n_processors] = 0
            #calculate in the new tact
            else:
                if real_time_queue[0].solution_time > tact_size:
                    real_time_queue[0].solution_time -= tact_size
                    in_processor[counter % n_processors] = 1
                    remained_time = 0
                    time += tact_size
                else:
                    time += real_time_queue[0].solution_time
                    Statistic['average_wait_in_system'] += time - real_time_queue[0].time - real_time_queue[0].solution_time
                    Statistic['solved_tasks'] += 1
                    remained_time = tact_size - real_time_queue[0].solution_time
                    in_processor[counter % n_processors] = 0
                    del real_time_queue[0]
            counter++
        #if real queue is empty add remained time and start next tact
        else:
            if remained_time != 0:
                Statistic['free_time'] += remained_time
                time += remained_time
                remained_time = 0
        #add tact time to system time if no tasks in current tact
            else:
                Statistic['free_time'] += tact_size
                time += tact_size

    #print(time, number_of_tasks * tact_size)
    Statistic['average_wait_in_system'] = Statistic['average_wait_in_system'] / Statistic['solved_tasks']
    Statistic['average_queue_length'] = sum(Statistic['average_queue_length']) / number_of_tasks
    return Statistic

def Execute(lambda_p, size, avg_sol_time, range1, tact_size, type_smo):
    period = numpy.random.poisson(lambda_p, size)
    period_k= [period[j] for j in range(len(period)) if not j % 3]
    period_k=numpy.array(period_k)
    queue = GenerateQueue(period, avg_sol_time, range1, tact_size)
    Stats  = SMO(queue, tact_size, size, type_smo)
    print("SMO type: ",type_smo)
    print("Intensity: ",lambda_p)
    print("Number of tasks : {} Solved : {}".format(sum(period), Stats['solved_tasks']))
    return Stats

def CreateGraph(type_smo, tact_size,avg_solution_time,second_range, color):
    n = 3
    wait_time, queue_length, free_time = [], [], []
    for i in numpy.linspace(0.1, 10):
        one_smo = Execute(i, 100, avg_solution_time, second_range, tact_size, type_smo)
        wait_time.append(one_smo['average_wait_in_system'])
        queue_length.append(one_smo['average_queue_length'])
        free_time.append(one_smo['free_time'])


    figure1 = plt.figure(figsize=(10,5))
    figure1.canvas.set_window_title(type_smo)
    t_i = figure1.add_subplot(111)
    t_i.set_title("Залежність середнього часу очікування від інтенсивності потоку")
    t_i.set_xlabel('Інтенсивність')
    t_i.set_ylabel('Середній час очікування')
    t_i.plot(numpy.linspace(0.1, 10), wait_time, color = color)
    plt.subplots_adjust(wspace=0.1, hspace=1, bottom=0.1, top=0.9)
    plt.show()


    figure2 = plt.figure(figsize=(10,5))
    figure2.canvas.set_window_title(type_smo)
    w_ql = figure2.add_subplot(111)
    w_ql.set_title("Залежність середньої довжини черги від середнього часу очікування")
    w_ql.set_xlabel('Середня довжина черги')
    w_ql.set_ylabel('Середній час очікування')
    w_ql.plot(sorted(queue_length), wait_time, color = color)
    plt.subplots_adjust(wspace=0.1, hspace=1, bottom=0.1, top=0.9)
    plt.show()
    

    figure3 = plt.figure(figsize=(10,5))
    figure3.canvas.set_window_title(type_smo)
    f_p = figure3.add_subplot(111)
    f_p.set_title("Залежність часу простою процесора від інтенсивності потоку")
    f_p.set_xlabel('Інтенсивність')
    f_p.set_ylabel('Час простою')
    f_p.plot(numpy.linspace(0.1, 10), free_time, color = color)
    plt.subplots_adjust(wspace=0.1, hspace=1, bottom=0.1, top=0.9)
    plt.show()


CreateGraph('RM', 1, avg_solution_time1,first_range, '#FF6289')
CreateGraph('EDF', 1, avg_solution_time2,second_range, '#FF084a')
