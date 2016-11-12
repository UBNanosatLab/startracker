import time, os, logging
from multiprocessing import Pipe, Queue, Process, log_to_stderr
from threading import Thread

DEFAULT_FEED_SIZE=100


logger=log_to_stderr()
logger.setLevel(logging.DEBUG)

feeds={}
subscribers={}
parent_pid=os.getpid()
parent_queue=Queue()
_parent_thread=None

def _parent():
	global feeds
	global subscribers
	terminating=False
	while not terminating:
		item=parent_queue.get()
		logger.info([time.time()]+item)
		try:
			if len(item)>1:
				eval(item[0])(*item[1:])
			else:
				exec(item[0])
		except Exception, e:
			logger.error([time.time()]+e)

def parent_cmd(*args):
	parent_queue.put(list(args))		

class feed:
	def __init__(self,feedname,size=DEFAULT_FEED_SIZE):
		global feeds
		self.size=size
		self.data = [[]]*size
		self.subscribers = {}
		self.full = 0
		self.cur = 0
		self.feedname=feedname
		if not feedname in feeds:
			feeds[feedname]=self
		if (os.getpid()!=parent_pid):
			parent_cmd("feed",feedname,size)

	def __getitem__(self,index):
		return self.data[self.cur-index-1]
	def publish(self,message):
		self.add(message)
		if (os.getpid()!=parent_pid):
			parent_cmd("feeds['"+self.feedname+"'].publish",message)
		else:
			for i in self.subscribers.values():
				i._writer.send(["feeds['"+self.feedname+"'].add",message])
	def add(self,x):
		self.data[self.cur] = x
		self.cur = (self.cur+1) % self.size
		if self.cur==0:
			self.full = 1
		return x
	def tolist(self):
		if self.full:
			r=self.data[self.cur:]+self.data[:self.cur]
		else:
			r=self.data[:self.cur]
		r.reverse()
		return r

class subscriber(Process):
	def __init__(self,target=None, args=[], **kws):
		global subscribers
		global _parent_thread
		assert(os.getpid()==parent_pid)
		Process.__init__(self, target=target, args=[self]+args, **kws)
			
		self.daemon=True
		subscribers[self.name]=self
		self._reader,self._writer=Pipe()
		self._child_thread=None
		self.subscriptions={}
		if _parent_thread is None:
			_parent_thread=Thread(target=_parent)
			_parent_thread.daemon=True
			_parent_thread.start()

	def cmd(self,*args):
		parent_cmd("subscribers['"+self.name+"']._writer.send",list(args))

	#warning - this is not thread/process safe!
	def _reval(self,statement):
		self.cmd("self._reader.send("+statement+")")
		return self._writer.recv()

	@staticmethod
	def _exec(self,statement):
		exec(statement)

	def _sub(self,feedname,size):
		global feeds
		self.subscriptions[feedname]=None
		if not feedname in feeds:
			feeds[feedname]=feed(feedname,size)
		feeds[feedname].subscribers[self.name]=self

	def _unsub(self,feedname):
		global feeds
		if feedname in self.subscriptions:
			feeds[feedname].subscribers.pop(self.name)
			self.subscriptions.pop(feedname)
			
	def subscribe(self,feedname,size=DEFAULT_FEED_SIZE):
		self._sub(feedname,size)
		if (os.getpid()!=parent_pid):
			parent_cmd("subscribers['"+self.name+"'].subscribe",feedname,size)
		else:
			self.cmd("self._sub",feedname,size)
		return feeds[feedname]
			
	def unsubscribe(self,feedname):
		self._unsub(feedname)
		if (os.getpid()!=parent_pid):
			parent_cmd("subscribers['"+self.name+"'].unsubscribe",feedname)
		else:
			self.cmd("self._unsub",feedname)
	
	#@staticmethod disables automatic passing of self
	#this is necessary because we need to explicitly pass it when starting the thread
	
	@staticmethod
	def _child(self):
		global feeds
		global subscribers
		terminating=False
		while not terminating:
			item=self._reader.recv()
			logger.debug([time.time()]+item)
			try:
				if len(item)>1:
					eval(item[0])(*item[1:])
				else:
					exec(item[0])
			except Exception, e:
				logger.error([time.time()]+ e)
		self._reader.close()
				
	def run(self):
		self._child_thread=Thread(target=subscriber._child,args=[self])
		self._child_thread.start()
		Process.run(self)
		self._child_thread.join()
	
	def terminate(self):
		global subscribers
		global _parent_thread
		if (os.getpid()!=parent_pid):
			parent_cmd("subscribers['"+self.name+"'].terminate()")
		else:
			for i in self.subscriptions.values():
				self.unsubscribe(i)
			parent_cmd("subscribers['"+self.name+"']._writer.send(['terminating=True'])\nsubscribers['"+self.name+"']._writer.close()\nsubscribers.pop('"+self.name+"')")
			Process.terminate(self)
			if len(subscribers)==0:
				parent_cmd("terminating=True")
				_parent_thread=None
