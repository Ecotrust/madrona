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

The ``lingcod.async`` app makes many of the typical interactions with `Celery <http://celeryproject.org/>`_ 
simpler as the ``lingcod.async`` app provides the ability to store and retrieve process results based on a 
url (as it is often the case that the same url request expects the same result), as well as making common 
Celery requests and interactions such as checking the status or retrieving the results of a task easier by 
abstracting away the need to manually digging through the celery tables yourself.  

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
to ``async.check_status_or_begin`` with the task method, the task method arguments, and a flag  will suffice.

.. code-block:: python

    from my_app import tasks
    status_text, task_id = tasks.check_status_or_begin(tasks.add, task_args=(3,5))
    
The above call returns an id that helps to identify the process for later retrieval.  Rather than force
you to store this ``task_id`` somewhere for later use, it may be more useful to utilize the url that 
triggered this process in the first place.

.. code-block:: python

    from my_app import tasks
    url = request.META['PATH_INFO']
    status_text, task_id = tasks.check_status_or_begin(tasks.add, task_args=(3,5), polling_url=url)
    
The advantage to this url strategy is that there is often a one-to-one correlation between 
a url and an expected result.  When the same url is accessed, such as ``<your-domain>/add/3/5/``,
``async`` methods can be used to help determine whether the process associated with that url has already been 
completed and can be retrieved for the user (without running the process again), or whether the process is 
still running and the user should receive some sort of 'process is still running...' message.  For the most 
part, methods in the ``async`` app have been configured to use both task ids and polling urls as identifiers 
(or keys) to a process.

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
        status_text, task_id = check_status_or_begin(tasks.add, task_args=(3,5), polling_url=url)
        return render_to_response(my_template, RequestContext( request, {'status': status_text} )) 
        
The above strategy allows the code to deal with the possibility that the process has already completed and the 
results are cached, or that the process is still running in the background, or that the process hasn't begun
at all.  If the results have already been cached, then they can be retrieved by the get_process_result method.  
In the other cases, the check_status_or_begin method will provide the user with an explanation relating to 
whether the process is still running or whether it just now begun.  In both of these latter cases, the task_id 
is returned as well in case you are wish to use that as an identifier rather than the url.  

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
  then your import command may not be structured correctly for your platform.  If ``result.status`` eventually
  returns ``STARTED`` or ``SUCCESS``, then your import command is structured correctly and should be written 
  as such in your code.      

lingcod.async API
-----------------

The following is a list of all the functions included with the ``async`` app.
   
  **check_status_or_begin(task_method, task_args=(), task_kwargs={}, polling_url=None, task_id=None, check_running=True, cache_results=True)**
    If check_running is left as True, this method begins the process only if the process is not already running.  
    
    .. note::
      
      In order to check whether the process is running or not, either a polling_url or a task_id must be passed.
      If neither is provided, the method assumes that this check should not be made.  
      
    If check_running is set to False (or if neither task_id, nor polling_url is provided), this method begins the 
    process.  In such cases, the function referred to by ``task_method`` will be called with the arguments included 
    in the ``task_args`` parameter.  If ``polling_url`` is given a value and ``cache_results`` remains set to 
    ``True``, then the ``polling_url`` can, in the future, be used as a key for cache retrieval.  
    
    .. note::
    
      This method does not check to see if the process has already been completed. The process_is_completed method
      can be used to check for process completion, and the get_process_result method can be used for retrieving
      the results. 
      
    The return values include a rendered template, explaining whether the process was already running,
    or has been started, and the task_id of that process.  
    
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
  

