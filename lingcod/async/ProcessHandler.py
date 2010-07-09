from models import URLtoTaskID
from djcelery.models import TaskMeta

'''
NOTES:
    url entries should be unique -- a single url maps to a single task_id in a one-to-one fashion
    this strategy allows the asynchronous models to serve as a cache for those apps that wish to use it as such

    begin_process assumes that the caller wants a new process to be run,
        even if the process has already been run
        even if the process has started, but not finished
    this way polling urls can remain unique
    if the caller wants the process to be run ONLY IF it hasn't been run already,
        the caller should first check with process_exists_in_cache
'''
#should also add a task_kwargs parameter in case the task has keyword parameters
def begin_process(polling_url, task_method, task_args, cache_results=False):
    #see if task exists already
    try:
        URLtoTaskID.objects.get(url=polling_url).delete()
    except:
        pass

    #initialize task
    task = task_method.delay(*task_args)
    #task_method(*task_args)
    #return 
    #if cache_results:
    URLtoTaskID(url=polling_url, task_id=task.task_id).save()
    return task.task_id
  
#returns boolean based on whether process is present (completed or not)
#Question:
#   how to handle this when celeryd is not running (temporarily shutdown for whatever reason)?
#   currently, it returns false 
#   this has the potential problem of the client requesting multiple identical processes 
#   which will all be executed once celerd is restarted (they will be queued up in ghettoq_message waiting for celeryd)
#Possible Solutions:
#   ignore the issue
#   remove from ghettoq_message when process is requested a second time
#   add third condition to if statement that checks for existence in ghettoq_message (process_is_queued_up)
#Problem:  
#   __get_task is returning None (for task) while process is running (should return the task with a pending/started status)
def process_exists_in_cache(polling_url=None, task_id=None):
    if process_is_running(polling_url, task_id) or process_is_complete(polling_url, task_id):
        return True
    else:
        return False
  
#Probably should get rid of this method now...
def process_has_begun(polling_url=None, task_id=None):
    try:
        URLtoTaskID.objects.get(url=polling_url)
        return True
    except:
        task = __get_task(polling_url, task_id)
        if task is not None:
            return True
        else:
            return False
  
#returns boolean based on whether process is in cache but not yet complete
def process_is_running(polling_url=None, task_id=None):
    result = __get_result(polling_url, task_id)
    if result is not None and result.status == 'PENDING': #might check for 'STARTED' as well
        return True
    else:
        return False
        
#returns boolean value based on result=='SUCCESS' from celery table
def process_is_complete(polling_url=None, task_id=None):
    task = __get_task(polling_url, task_id)
    if task is not None and task.status == 'SUCCESS':
        return True
    else:
        return False
    
#returns result.result from celery table
def get_process_result(polling_url=None, task_id=None):
    task = __get_task(polling_url, task_id)
    if task is not None:
        return task.result
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
    
#get the task record from celery_taskmeta   
#i wonder if we can get away with using __get_result instead...
def __get_task(polling_url=None, task_id=None):
    if polling_url == task_id == None:
        raise ValueError("Either polling_url or task_id must be passed a value")
    if task_id is None:
        task_id = get_taskid_from_url(polling_url)
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except:
        #raise ValueError("Requested task does not exist")
        return None
    return task
    
#get the AsyncResult object associated with the given (directly or indirectly) task_id
#(this object provides us access to the status field)
def __get_result(polling_url=None, task_id=None):
    if polling_url == task_id == None:
        raise ValueError("Either polling_url or task_id must be passed a value")
    if task_id is None:
        task_id = get_taskid_from_url(polling_url)
    from celery import result
    result = result.AsyncResult(task_id)
    if result.task_id == None:
        return None
    return result    
    

    