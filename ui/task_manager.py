# ui/task_manager.py

import logging
import traceback
from typing import Callable, Any, List, Tuple

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

class Worker(QObject):
    """
    一个通用的工作器 QObject，可以被移动到后台线程执行任务。
    它通过信号与主线程进行通信，确保线程安全。
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception, str)

    def __init__(self, task: Callable[..., Any], *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """
        当后台线程启动时，此槽函数会被自动调用以执行任务。
        """
        try:
            logger.debug(f"Worker starting task: {self.task.__name__}")
            result = self.task(*self.args, **self.kwargs)
            logger.debug(f"Worker finished task: {self.task.__name__}")
            self.finished.emit(result)
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"An error occurred in worker task '{self.task.__name__}':\n{tb_str}")
            self.error.emit(e, tb_str)


class TaskManager:
    """
    一个全局单例的任务管理器，用于轻松地在后台线程中运行耗时函数。
    它封装了 QThread 和 Worker 的创建、管理和生命周期，解决了对象被过早
    垃圾回收的关键问题。
    """
    def __init__(self):
        self.running_tasks: List[Tuple[QThread, Worker]] = []

    def run_in_background(
        self, 
        task: Callable[..., Any], 
        on_success: Callable[[Any], None] = None,
        on_error: Callable[[Exception, str], None] = None,
        *args, **kwargs
    ):
        """
        在后台线程中异步执行一个任务。
        """
        thread = QThread()
        worker = Worker(task, *args, **kwargs)
        worker.moveToThread(thread)

        task_reference = (thread, worker)
        self.running_tasks.append(task_reference)
        logger.debug(f"Task '{task.__name__}' appended. Currently running tasks: {len(self.running_tasks)}")

        thread.started.connect(worker.run)
        
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)

        thread.finished.connect(lambda: self._cleanup_task(task_reference))
        
        if on_success:
            worker.finished.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
            
        thread.start()

    def _cleanup_task(self, task_ref: Tuple[QThread, Worker]):
        """当任务完成时，从正在运行的列表中安全地移除它。"""
        try:
            self.running_tasks.remove(task_ref)
            logger.debug(f"Task cleaned up. Currently running tasks: {len(self.running_tasks)}")
        except ValueError:
            logger.warning("Attempted to clean up a task that was not in the running list.")

task_manager = TaskManager()