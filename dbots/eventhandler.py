# https://github.com/Rapptz/discord.py/blob/master/discord/client.py
# https://github.com/Fuyukai/curious/blob/0.8/curious/core/gateway.py

import asyncio
import logging

log = logging.getLogger(__name__)

class _ClientEventTask(asyncio.Task):
    def __init__(self, original_coro, event_name, coro, *, loop):
        super().__init__(coro, loop=loop)
        self.__event_name = event_name
        self.__original_coro = original_coro

    def __repr__(self):
        info = [
            ('state', self._state.lower()),
            ('event', self.__event_name),
            ('coro', repr(self.__original_coro)),
        ]
        if self._exception is not None:
            info.append(('exception', repr(self._exception)))
        return '<ClientEventTask {}>'.format(' '.join('%s=%s' % t for t in info))

class EventHandler:
    def __init__(self, loop = None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._listeners = {}

    def event(self, name_or_coro):
        event_name = name_or_coro
        if callable(name_or_coro):
            if not asyncio.iscoroutinefunction(name_or_coro):
                raise TypeError('event registered must be a coroutine function')
            else:
                event_name = name_or_coro.__name__[3:]
            if event_name in self._listeners:
                self._listeners[event_name].append(name_or_coro)
            else:
                self._listeners[event_name] = [name_or_coro]
            log.debug('%s has successfully been registered as an event', event_name)
            return name_or_coro
        else:
            def inner(coro): 
                if not asyncio.iscoroutinefunction(coro):
                    raise TypeError('event registered must be a coroutine function')
                if name_or_coro in self._listeners:
                    self._listeners[name_or_coro].append(coro)
                else:
                    self._listeners[name_or_coro] = [coro]
                log.debug('%s has successfully been registered as an event using named decorator', name_or_coro)
                return coro
            return inner 
        return

    async def _run_event(self, coro, event_name, *args, **kwargs):
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                log.error('A %s event handler failed to run', event_name)
            except asyncio.CancelledError:
                pass

    def _schedule_event(self, coro, event_name, *args, **kwargs):
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return _ClientEventTask(original_coro=coro, event_name=event_name, coro=wrapped, loop=self.loop)

    def dispatch(self, event, *args, **kwargs):
        log.debug('Dispatching event %s', event)
        method = 'on_' + event

        listeners = self._listeners.get(event)
        if listeners:
            for coro in listeners:
                self._schedule_event(coro, event, *args, **kwargs)

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, event, *args, **kwargs)