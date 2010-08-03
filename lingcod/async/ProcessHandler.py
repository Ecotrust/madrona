from models import URLtoTaskID
from djcelery.models import TaskMeta
from django.template.loader import render_to_string

"""
NOTES:
    url entries should be unique -- a single url maps to a single task_id in a one-to-one fashion
    this strategy allows the asynchronous models to serve as a cache for those apps that wish to use it as such

    check_status_or_begin does not check to see if process is already complete
    if the caller wants the process to be run ONLY IF it hasn't been completed already,
    the caller should check process_is_complete instead
    
    process_is_running (called on its own or from check_status_or_begin or process_is_running_or_complete) checks
    only if status == 'STARTED', this seems like the safest strategy although it does have it's shortcomings.
    When a task is triggered, it is stored in the celery_taskmeta table with status == PENDING, as soon as 
    a worker is assigned to that task, the status becomes STARTED, when the task is complete, status becomes SUCCESS.
    If something goes wrong during the STARTED phase (celeryd is shut down, etc), then status becomes FAILURE. 
    If celeryd is not communicating with ghettoq, or not running at all, then the status will remain as PENDING.
    If we assume that PENDING means STARTED, then we may be mislead into thinking a task is being processed, 
    when in fact it is sitting idle.  This may only become apparent after waiting way-too-long for the task
    to complete.  
    If we only check for STARTED, then each time the task is requested, we will add a new task to the queue.  This
    may back up the queue, but only in situations when there is something wrong to begin with.  This will also
    likely alert the user (or the developer) more immediately that something has gone wrong with celeryd (or ghettoq,
    or whatever) since the returned statement will be something like 'the process has begun', even with subsequent
    requests which should have changed the statement to something like 'the process is already running'.  There is
    also the slight chance that a task will be requested in such quick succession that a worker will not yet be assigned
    to that task and the status will still be PENDING, in which case a new task will be added to the queue.  This seems
    a small price to pay for the more immediate recognition that there is indeed a problem.  As the developer in this
    case, I'd rather get the impression of a False Negative (thinking there may be a problem, when in fact there is none),
    than a False Positive (given the impression that everything is fine, when in fact there is a problem).  Also, the 
    user is more likely to notice a problem sooner in the case when there is a hint in the returned statement (that
    the process has begun...yet again), than in the case when they must figure out there is a problem only because
    the process is taking an inordinately long time (in many cases this could mean hours rather than minutes).  
"""

'''
begin_process starts the background process
if the process has already been run, the related URLtoTaskID entry is cleared and re-calculated
if the process is currently running, the related URLtoTaskID entry is cleared, and the process is started again
(in this case more than one identical process may be running at the same time -- to prevent this see NOTES above)
called by check_status_or_begin
'''
def __begin_process(task_method, task_args=(), task_kwargs={}, polling_url=None, cache_results=True):
    #see if task exists already
    try:
        URLtoTaskID.objects.get(url=polling_url).delete()
    except:
        pass
    #initialize task
    task = task_method.delay(*task_args, **task_kwargs)
    if polling_url and cache_results:
        URLtoTaskID(url=polling_url, task_id=task.task_id).save()
    return task.task_id

'''
check_status_or_begin
if the user has supplied neither the polling_url nor the task_id, it is assumed that they wish to start the process
(since no process_is_running check can be made without a process identifier anyway)
otherwise, if check_running is left to its default value of True, then a check will be made to see if the process is
already running, in which case a related message is returned to the user and the process is not re-started
if the process is not already running (or the user doesn't wish to check for that case), then the process will be
added to the queue, and a message indicating the process has begun will be returned to the user
if the process had already completed (status == SUCCESS rather than STARTED), it will be run again
if the caller wants the process to be run ONLY IF it hasn't been completed already,
the caller should check process_is_complete instead
'''
def check_status_or_begin(task_method, task_args=(), task_kwargs={}, polling_url=None, task_id=None, check_running=True, cache_results=True):
    if polling_url is None and task_id is None:
        check_running = False
    if check_running and process_is_running(polling_url, task_id):
        if task_id is None:
            task_id = get_taskid_from_url(polling_url)
        return render_to_string('already_processing.html', {}), task_id
    else:
        task_id = __begin_process(task_method, task_args, task_kwargs, polling_url)
        return render_to_string('starting_process.html', {}), task_id
  
#returns boolean based on process.status == 'STARTED' or 'SUCCESS' (currently running or complete)
def process_is_running_or_complete(polling_url=None, task_id=None):
    if process_is_running(polling_url, task_id) or process_is_complete(polling_url, task_id):
        return True
    else:
        return False
  
#returns boolean based on whether process is in cache and marked as STARTED
def process_is_running(polling_url=None, task_id=None):
    result = __get_asyncresult(polling_url, task_id)
    if result is not None and result.status == 'STARTED': 
        return True
    else:
        return False
        
#returns boolean value based on result=='SUCCESS' from celery table
def process_is_complete(polling_url=None, task_id=None):
    result = __get_asyncresult(polling_url, task_id)
    if result is not None and result.status == 'SUCCESS':
        return True
    else:
        return False
    
#returns result.result from celery table
def get_process_result(polling_url=None, task_id=None):
    result = __get_asyncresult(polling_url, task_id)
    if result is not None:
        return result.result
    else:
        return None
    
#get task_id from URLtoTaskID table
def get_taskid_from_url(polling_url):
    try:
        entry = URLtoTaskID.objects.get(url=polling_url)
        return entry.task_id
    except:
        #raise ValueError("Given URL does not map to any known task_id")
        return None
    
#get url from URLtoTaskID table    
def get_url_from_taskid(task_id):
    try:
        entry = URLtoTaskID.objects.get(task_id=task_id)
    except:
        raise ValueError("Given task_id does not map to any known URL")
    return entry.url

#get the AsyncResult object associated with the given (directly or indirectly) task_id
#(this object provides us access to the status field)
def __get_asyncresult(polling_url=None, task_id=None):
    if polling_url == task_id == None:
        raise ValueError("Either polling_url or task_id must be passed a value")
    if task_id is None:
        task_id = get_taskid_from_url(polling_url)
    from celery import result
    result = result.AsyncResult(task_id)
    if result.task_id == None:
        return None
    return result    
    

    