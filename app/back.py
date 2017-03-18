import threading
import time
import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter

class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something

            allrunningid_cpu = []

            ec2 = boto3.resource('ec2')  # 检差正在running的实例
            instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            for instance in instances:
                allrunningid_cpu.append(instance.id)  # instance id save in list

            totalrunnumber_cpu = len(allrunningid_cpu)  # num of running instance

            xixi = 1
            haha = 0

            cpu_utilizationlist = []

            while xixi <= totalrunnumber_cpu:
                ec2 = boto3.resource('ec2')
                instance = ec2.Instance(allrunningid_cpu[haha])
                # instances = ec2.instances.all()
                client = boto3.client('cloudwatch')

                metric_name = 'CPUUtilization'
                namespace = 'AWS/EC2'
                statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

                cpu = client.get_metric_statistics(
                    Period=1 * 60,
                    StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
                    EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
                    MetricName=metric_name,
                    Namespace=namespace,  # Unit='Percent',
                    Statistics=[statistic],
                    Dimensions=[{'Name': 'InstanceId', 'Value': allrunningid_cpu[haha]}]
                )

                cpu_stats = []

                for point in cpu['Datapoints']:
                    hour = point['Timestamp'].hour
                    minute = point['Timestamp'].minute
                    time1 = hour + minute / 60
                    cpu_stats.append([time1, point['Average']])

                cpu_stats = sorted(cpu_stats, key=itemgetter(0))

                aaa = cpu_stats[-1]
                bbb = aaa[1]
                print(bbb)
                cpu_utilizationlist.append(bbb)

                xixi = xixi + 1
                haha = haha + 1

            print(cpu_utilizationlist)
            print('Doing something imporant in the background')
            time.sleep(self.interval)

example = ThreadingExample()
#time.sleep(20)
#print('Checkpoint')
#time.sleep(10)
#print('Bye')