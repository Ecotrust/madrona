.. _async_app:

Async App
=========

MarineMap includes a strategy for runnning lengthy processes in the background.  
To implement this strategy we use `Celery <http://celeryproject.org/>`_ as our distributed 
task queue, and we created the ``lingcod.async`` app for easy exchanges between the Celery tables 
and the codebase.  For more information on how to get Celery working on your machine, see the 
:ref:`Asynchronous Task Queue<async_task_queue>` documentation.

Overview
********

The ``lingcod.async`` app has been created to abstract some of the boilerplate coding details out of 
the `Celery <http://celeryproject.org/>`_ interactions and to provide a more straightforward 
API for checking the status of processes (are they currently running, or have they already been completed),
retrieving the cached results of processes, and running processes asynchronously (in the background).  

.. note::

  If `Celery <http://celeryproject.org/>`_ is not yet set up for your machine, you'll want to see the 
  :ref:`Asynchronous Task Queue<async_task_queue>` documentation to get Celery up and running.

How to Use the Async App
************************

First, you will want to add a ``tasks.py`` file to the app that contains the process you want to
run asynchronously.  This file will house the tasks that will be called by the ``async`` app, and 
each of the tasks should define a discrete operation that will be tagged as such (``@task``) so that
they will be registered with Celery when the ``celeryd`` process is started.  

The following shows a sample ``tasks.py`` with a simple ``add`` method that may be useful for testing:

.. code-block:: python

    from celery.decorators import task
    
    @task
    def add(x, y):
        return x + y

Once you have a ``tasks.py``, you'll be able to utilize the ``async`` app to start your tasks, 
check their status, and retrieve their results.  

Basic Uses
----------

Often times, you'll want to simply run a process in the background.  In these cases a simple call
to ``async.begin_process`` with the task method and the task method arguments will suffice.

.. code-block:: python

    from my_app import tasks
    task_id = begin_process(tasks.add, task_args=(3,5))
    
The above call returns an id that helps to identify the process for later retrieval.  Rather than force
you to store this ``task_id`` somewhere for later use, it may be more useful to utilize the url that 
triggered this process in the first place.

.. code-block:: python

    from my_app import tasks
    url = request.META['PATH_INFO']
    begin_process(tasks.add, task_args=(3,5), polling_url=url)
    
The advantage to this url strategy is that there is often a one-to-one correlation between 
a url and an expected result.  When the same url is accessed, such as ``<your-domain>/add/3/5/``,
``async`` methods can be used to help determine whether the process associated with that url has completed 
and can be retrieved for the user, or whether the process is still running and the user should receive some 
sort of 'process is still running...' message.  For the most part, methods in the ``async`` app have been 
configured to use both task ids and polling urls as identifiers to a process.

A common flow of control may be as follows:

.. code-block:: python

    #get the url that caused this view to execute
    url = request.META['PATH_INFO']
    #check to see if the requested process has been run already
    if process_is_complete(url):
        return HttpResponse(str(get_process_result(url)))
    else: 
        #start the process or continue to wait for the process to complete
        from my_app import tasks
        status_text = check_status_or_begin(tasks.add, task_args=(3,5), polling_url=url)
        return render_to_response(my_template, RequestContext( request, {'status': status_text} )) 
        
The above strategy allows the code to deal with the possibility that the process has already completed and cached 
the results, or that the process is still running in the background, or that the process hasn't begun
at all.  In each case a respone will be returned, either containing the result of the process, or providing
the user with an explanation relating to whether the process is still running or that it just now begun.  

.. note::

  The manner in which the import tasks statement is structured is very important to Celery.
  Where one of the following strategies may work on one machine or platform, the other strategy might be 
  necessary on another machine or platform.  
    
  .. code-block:: python
    
    >>>from my_proj.my_app.tasks import add 
    >>>result = add.delay(2,2)
    >>>result.status
    PENDING
    
    >>>from my_proj.my_app import tasks
    >>>result = tasks.add.delay(2,2)
    >>>result.status
    SUCCESS
    
  If the process seems to register with Celery but never completes (status equals ``PENDING`` and never changes), 
  then your import command is not structured correctly for your platform.  If ``result.status`` eventually
  returns ``STARTED`` or ``SUCCESS``, then your import command is structured correctly and should be written 
  as such in your code.      

lingcod.async API
-----------------

The following is a list of all the functions included with the ``async`` app.

  **begin_process(task_method, task_args=(), task_kwargs={}, polling_url=None, cache_results=True)**
    This method forces a process to start running in the background (it does not check to see if that
    process is currently running or not).
    
    If ``polling_url`` is given a value and ``cache_results`` remains set to ``True``, then the ``polling_url`` 
    is used as a key for cache retrieval.  
    
    A unique task id is returned.  This task id and the polling url can both be used to retrieve the status
    and results via the methods below.  
       
  **check_status_or_begin(task_method, task_args=(), task_kwargs={}, polling_url=None, task_id=None, cache_results=True)**
    This method begins the process if the process is not marked as ``PENDING`` in the task queue.  
    
    Either the polling url or the task id is necessary to identify the process.  If the process is not
    marked as ``STARTED``, then the function referred to by ``task_method`` will be called with the arguments 
    included in the ``task_args`` parameter.  
    
  **process_is_running_or_complete(polling_url=None, task_id=None)**
    This method takes either the polling url or the task id as a unique identifier.  
    
    Returns ``True`` if the process is currently running, or if the process is complete.

  **process_is_running(polling_url=None, task_id=None)**
    This method takes either the polling url or the task id as a unique identifier.  
    
    Returns ``True`` if the process is running (``status=='STARTED'``).
  
  **process_is_complete(polling_url=None, task_id=None)**
    This method takes either the polling url or the task id as a unique identifier.  
    
    Returns ``True`` if the process is complete (``status=='SUCCESS'``).
  
  **get_process_result(polling_url=None, task_id=None)**
    This method takes either the polling url or the task id as a unique identifier.  
    
    Returns the cached result of the process.
  
  **get_taskid_from_url(polling_url=None)**
    This method takes a polling url and returns the related task id.
  
  **get_url_from_taskid(task_id=None)**
    This method takes a task id and returns the related polling url.
  

