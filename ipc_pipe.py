# -*-coding: utf-8 -*-


import multiprocessing

def consumer(pipe):
    output_p, input_p = pipe
    input_p.close()

    while True:
        try:
            item = output_p.recv()
        except EOFError:
            break
        print(item)
    print('Consume done')


def producer(sequence, input_p):
    for item in sequence:
        input_p.send(item)


if __name__ == '__main__':
    output_p, input_p = multiprocessing.Pipe()

    cons_p = multiprocessing.Process(target=consumer, args=((output_p, input_p),))
    cons_p.start()

    output_p.close()

    sequence = [1, 2, 3, 4]
    producer(sequence, input_p)

    input_p.close()

    cons_p.join()
