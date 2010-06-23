.. _async_task_queue:

Asynchronous Task Queue 
=======================
Celery is an asynchronous task queue/job queue based on distributed message passing. It is focused on real-time operation, but supports scheduling as well.

http://ask.github.com/celery/getting-started/introduction.html

Installation
------------
The requirements are easy_installable since we;re using ghettoq instead of the more powerful but complicated RabbitMQ::

    sudo pip install ghettoq
    sudo pip install celery

Settings
--------
In the simplest case, we can just add the apps and point them to use the current django db settings::

    CARROT_BACKEND = "ghettoq.taproot.Database" 
    CELERY_RESULT_BACKEND = 'database'
    INSTALLED_APPS += ( 'celery', 'ghettoq' )

After that, make sure to run `python manage.py syncdb`

Writing your tasks
------------------
Just a normal python function with a decorator::

	from celery.decorators import task
	@task(rate_limit='4/m')
	def get_shps(name, **kwargs):
	   logger = get_shps.get_logger(**kwargs)
	   logger.info("Starting the task")
           polygons = some_long_process(name)
	   return polygons

rate_limit sets the frequency of task exceution (in this case 4 tasks per minute or '4/m')

Beware of 'unpicklable' objects getting passed around.

Periodic tasks
--------------
Like a cron job. Requires that you start the celeryd service with a 'heartbeat'::

    from celery.decorators import periodic_task
    from datetime import timedelta
    @periodic_task(run_every=timedelta(seconds=30))
    def do_stuff(**kwargs):
        clean_up_temp_files()
        return True

Executing tasks
---------------
You can call the task directly to run syncronously::

    x = get_shps('test')

Or you can do it async via the task queue::

    ax = get_shps.delay('test')

The result of the async call can be monitored and the result retrieved when ready::

    ax.status # u'PENDING'
    ax.status # u'SUCCESS'
    ax.ready() # True or False
    ax.result # The polygon objects returned by the task

    
Running the celeryd service
---------------------------
This has to be running to execute the jobs. If, for whatever reason, the celeryd service is stopped, jobs can still get added to the queue but wont get run
until the celeryd process is fired up again. 

You can run it from the command line in a terminal::

	python manage.py celeryd -v 2 -l DEBUG -c 1 -B -E

Note the -B flag to turn on the 'hearbeat' for periodic tasks, the -c 1 which limits the operation to a single cpu

For production environments, use an init.d script. And example is in the code repository at marinemap/apache/celeryd. Instructions are contained in the comments of that file.
