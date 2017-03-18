from flask import render_template, redirect, url_for, request, g
from app import webapp
import threading
import time
import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter
import mysql.connector

from app.config import db_config

code = '0'
title= '0'
description= '0'
shrinkratio= '0'
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


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


            growthreshold = int(code)
            shrinkthreshold = int(title)
            exradio = int(description)
            shradio = int(shrinkratio)
            print(growthreshold)
            print(shrinkthreshold)
            print(exradio)
            print(shradio)

            sum = growthreshold + shrinkthreshold +exradio + shradio
            print(sum)

            allrunningid_cpu = []

            ec2 = boto3.resource('ec2')  # 检差正在running的实例
            instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            for instance in instances:
                allrunningid_cpu.append(instance.id)  # instance id save in list
            if 'i-0b3cd01b9efed2ba8' in allrunningid_cpu:
                allrunningid_cpu.remove('i-0b3cd01b9efed2ba8')
            if 'i-08b0d46529d238909' in allrunningid_cpu:
                allrunningid_cpu.remove('i-08b0d46529d238909')

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
            needworkerpool_num = totalrunnumber_cpu * exradio - totalrunnumber_cpu
            print(needworkerpool_num)

            if not cpu_utilizationlist:
                cpu_utilizationlist.append(0)

            if max(cpu_utilizationlist)> growthreshold and needworkerpool_num >= 1 and growthreshold >50 and growthreshold<99:
                 ######################    成倍数增加instance
                i = 1
                while i <= needworkerpool_num:

                    ec2 = boto3.resource('ec2')
                    client = boto3.client('elb')
                    userdata = """#cloud-config

                        runcmd:
                         - git clone https://974153457:lixingjiu1992@github.com/974153457/imagetrickfinal.git /home/ubuntu/Desktop/ece1779a1
                         - cd /home/ubuntu/Desktop
                         - sudo chmod -R 777 ece1779a1
                         - cd ece1779a1
                         - sudo rm -rf venv
                         - cp -r /home/ubuntu/Desktop/ece1779/databases/venv/ .
                         - sudo cp credentials /home/ubuntu/.aws
                         - sudo cp config /home/ubuntu/.aws
                         - su -c './venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 -D app:webapp' -s /bin/sh ubuntu

                        """

                    xindeinstance = ec2.create_instances(ImageId=config.ami_id,
                                                         MinCount=1,
                                                         MaxCount=1,
                                                         KeyName='ece1779winter_as1',
                                                         UserData=userdata,
                                                         InstanceType='t2.small',
                                                         SubnetId='subnet-f52970ae',
                                                         Monitoring={'Enabled': True},
                                                         SecurityGroupIds=['sg-85565cf9']
                                                         )
                    for x in xindeinstance:
                        xindeID = x.id
                        print(xindeID)

                    response = client.register_instances_with_load_balancer(
                        Instances=[
                            {
                                'InstanceId': xindeID,
                            },
                        ],
                        LoadBalancerName='loadbalancertest',
                    )

                    xindeinstance = None
                    response = None
                    ec2 = None
                    client = None
                    i = i + 1

                print("creat some new worker pool")



            needshrinkworkerpool_num = 0
            if shradio >= 2:
                needshrinkworkerpool_num = totalrunnumber_cpu - totalrunnumber_cpu * 1 / shradio
                print(needshrinkworkerpool_num)

            if max(cpu_utilizationlist) < shrinkthreshold and needshrinkworkerpool_num >= 1 and shrinkthreshold >20 and shrinkthreshold <51:
                allrunningid2 = []

                ec2 = boto3.resource('ec2')  # 检差正在running的实例
                instances = ec2.instances.filter(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
                for instance in instances:
                    print(instance.id)
                    allrunningid2.append(instance.id)  # instance id save in list

                print(allrunningid2)

                  # num of running instance



                if 'i-0b3cd01b9efed2ba8' in allrunningid2:
                    allrunningid2.remove('i-0b3cd01b9efed2ba8')
                if 'i-08b0d46529d238909' in allrunningid2:
                    allrunningid2.remove('i-08b0d46529d238909')


                print(allrunningid2)
                totalrunnumber = len(allrunningid2)   # num of running instance

                ii = 1
                a = totalrunnumber-1
                while ii <= needshrinkworkerpool_num:
                    ec2 = boto3.resource('ec2')

                    ec2.instances.filter(InstanceIds=[allrunningid2[a]]).terminate()

                    ii = ii + 1
                    a = a - 1


            time.sleep(self.interval)
example = ThreadingExample()








@webapp.route('/ec2_examples', methods=['POST'])
# Create a new student and save them in the database.
def parameters():
    global code
    global title
    global description
    global shrinkratio
    code = request.form.get('code', "")
    title = request.form.get('title', "")
    description = request.form.get('description', "")
    shrinkratio = request.form.get('shrinkratio',"")

    error = False

    if code == "" or title == "" or description == "" or shrinkratio == "":
        error = True
        error_msg = "Error: All fields are required!"


    if error :
        return render_template("ec2_examples/list.html", title="New Course", error_msg=error_msg,  ctitle=title,
                               description=description,shrinkratio=shrinkratio)

    #print(code)
    #print(title)
    #print(description)
    #print(shrinkratio)
    #x = int(code)+int(title)
    #print(x)

    return redirect(url_for('ec2_list'))




@webapp.route('/ec2_examples',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

#    instances = ec2.instances.filter(
#        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = ec2.instances.all()

#    for x in instances:
#        print(x.id)

    return render_template("ec2_examples/list.html",title="EC2 Instances",instances=instances)



@webapp.route('/ec2_examples/delete',methods=['POST'])
def deletealldata():
    cnx = get_db()
    cursor = cnx.cursor()

    query = "DELETE FROM users "

    cursor.execute(query)
    cnx.commit()
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    #   s3.create_bucket(Bucket='papapapapa')
    for peter in s3.buckets.all():
        print(peter.name)
    # Print out bucket names


    for bucket in s3.buckets.all():

        for key in bucket.objects.all():
            print(key.key)
            key.delete()
        bucket.delete()
    return redirect(url_for('ec2_list'))






@webapp.route('/ec2_examples/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))


    return render_template("ec2_examples/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@webapp.route('/ec2_examples/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')
    client = boto3.client('elb')

    userdata = """#cloud-config

    runcmd:
     - git clone https://974153457:lixingjiu1992@github.com/974153457/imagetrickfinal.git /home/ubuntu/Desktop/ece1779a1
     - cd /home/ubuntu/Desktop
     - sudo chmod -R 777 ece1779a1
     - cd ece1779a1
     - sudo rm -rf venv
     - cp -r /home/ubuntu/Desktop/ece1779/databases/venv/ .
     - sudo cp credentials /home/ubuntu/.aws
     - sudo cp config /home/ubuntu/.aws
     - su -c './venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 -D app:webapp' -s /bin/sh ubuntu

    """

    xindeinstance = ec2.create_instances(ImageId=config.ami_id,
                         MinCount=1,
                         MaxCount=1,
                         KeyName='ece1779winter_as1',
                         UserData = userdata,
                         InstanceType='t2.small',
                         SubnetId='subnet-f52970ae',
                         Monitoring = {'Enabled':True},
                         SecurityGroupIds=['sg-85565cf9']
                         )
    for x in xindeinstance:
        xindeID = x.id
        print(xindeID)

    response = client.register_instances_with_load_balancer(
        Instances=[
            {
                'InstanceId': xindeID ,
            },
        ],
        LoadBalancerName='loadbalancertest',
    )
    print(response)


    return redirect(url_for('ec2_list'))



@webapp.route('/ec2_examples/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))


@webapp.route('/ec2_examples/managerlogin',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def managerlogin():
    return render_template("ec2_examples/managerlogin.html",title="Manager Login")


@webapp.route('/ec2_examples/managerlogin', methods=['POST'])
# Create a new student and save them in the database.
def managerlogin_save():


    a = request.form.get('login', "")
    title = request.form.get('passwords', "")

    error = False

    if a == "" or title == "" :
        error = True
        error_msg = "Error: All fields are required!"

    if error:
        return render_template("ec2_examples/managerlogin.html", title="Manager Login", error_msg=error_msg, login=a, passwords=title)

    if a == 'admin':
        return redirect(url_for('ec2_list'))
    else:
        error_msg = "Error:Wrong Manager User Name"
        return render_template("ec2_examples/managerlogin.html", title="Manager Login", error_msg=error_msg, login=a,
                               passwords=title)

