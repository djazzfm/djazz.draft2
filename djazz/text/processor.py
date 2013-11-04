

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class ProcessorError(Exception):
    pass


class Processor(object):
    
    ESCAPE_CHAR = '!'
    NL_CHAR = '\n'
    
    COMPILE_OPEN_TAG = '[>'
    COMPILE_CLOSE_TAG = '<]'
    
    IMACRO_OPEN_TAG = '[> '
    IMACRO_CLOSE_TAG = ' <]'
    
    MACRO_OPEN_TAG = '[>> '
    MACRO_CLOSE_TAG = '<<]'
    
    MACRO_BLOCK = 0
    MACRO_INLINE = 1
    
    
    class MacroError(Exception):
        pass
    
    
    def __init__(self):
        self.macros = {}
        self.inline_macros = {}
    
    
    def inline_macro_register(self, name, func):
        if name in self.inline_macros:
            m = "inline_macro '%s' is already registered" % name
            raise AlreadyRegistered(m)
        self.inline_macros[name] = func
    
    def inline_macro_unregister(self, name):
        if not name in self.inline_macros:
            m = "inline_macro '%s' is not registered" % name
            raise NotRegistered(m)
        del self.inline_macros[name]
    
    def inline_macro(self, name, func=None):
        def decorate(func):
            self.inline_macro_register(name, func)
            return func
        
        if not func:
            return decorate
        
        self.inline_macro_register(name, func)
    
    
    
    def macro_register(self, name, func):
        if name in self.macros:
            m = "macro '%s' is already registered" % name
            raise AlreadyRegistered(m)
        self.macros[name] = func
    
    def macro_unregister(self, name):
        if not name in self.macros:
            m = "macro '%s' is not registered" % name
            raise NotRegistered(m)
        del self.macros[name]
    
    def macro(self, name, func=None):
        def decorate(func):
            self.macro_register(name, func)
            return func
        
        if not func:
            return decorate
        
        self.macro_register(name, func)
    
    
    
    def escape(self, text, cursor):
        c = text[cursor]
        
        if not c == self.ESCAPE_CHAR or len(text) <= cursor:
            return c, cursor
        
        nc = text[cursor+1]
        if nc == self.ESCAPE_CHAR or \
           text[cursor+1:].startswith(self.IMACRO_OPEN_TAG) or \
           text[cursor+1:].startswith(self.IMACRO_CLOSE_TAG) or \
           text[cursor+1:].startswith(self.MACRO_OPEN_TAG) or \
           text[cursor+1:].startswith(self.MACRO_CLOSE_TAG):
            return text[cursor+1], cursor + 1
        else:
            return c, cursor
    
    
    def compile_macro(self, text, cursor, stack):
        
        if self.MACRO_OPEN_TAG == self.IMACRO_OPEN_TAG and \
           self.MACRO_CLOSE_TAG == self.IMACRO_CLOSE_TAG:
            raise ProcessorError("Identical open and close tags")
        
        # Not a macro
        if not text[cursor:].startswith(self.MACRO_OPEN_TAG):
            return text[cursor], cursor
        
        # Getting head
        head = ''
        cursor += len(self.MACRO_OPEN_TAG)
        while cursor < len(text):
            c = text[cursor]
            head += c
            cursor += 1
            if c == self.NL_CHAR: break
        
        head = head.strip()
        
        content = ''
        while cursor < len(text):
            c = text[cursor]
            pc = text[cursor - 1]
            
            if pc == self.NL_CHAR and \
               text[cursor:].startswith(self.MACRO_CLOSE_TAG):
                cursor += (len(self.MACRO_CLOSE_TAG) - 1)
                
                if not text[cursor+1] == self.NL_CHAR:
                    raise self.MacroError("New line expected")
                
                seq = '\x00' + str(len(stack)) + '\x01'
                
                splitted = head.lstrip().split(' ', 1)
                macro_name = splitted[0]
                macro_args = []
                if len(splitted) > 1:
                    macro_args = splitted[1:]
                
                stack.append([self.MACRO_BLOCK,
                              macro_name,
                              macro_args,
                              content])
                
                return seq, cursor
            
            content += c
            cursor += 1
        
        raise self.MacroError("Unclosed macro")
    
    
    def compile_imacro(self, text, cursor, stack):
        
        if not text[cursor:].startswith(self.IMACRO_OPEN_TAG):
            return text[cursor], cursor

        seq = ''
        cursor += len(self.IMACRO_OPEN_TAG)
        while cursor < len(text):
            c = text[cursor]
            
            if c == self.ESCAPE_CHAR:
                processed, cursor = self.escape(text, cursor)
                seq += processed
            
            elif text[cursor:].startswith(self.IMACRO_CLOSE_TAG):
                cursor += (len(self.IMACRO_CLOSE_TAG) - 1)
                compiled = '\x00' + str(len(stack)) + '\x01'
                splitted = seq.lstrip().split(' ', 1)
                item = [self.MACRO_INLINE, splitted[0]]
                if len(splitted) > 1:
                    item.append(splitted[1])
                stack.append(item)
                return compiled, cursor
            
            else: seq += c
            
            cursor += 1
        
        raise self.MacroError("Unclosed macro")
    
    
    
    def compile(self, text):
        c = None   # current char
        pc = None  # previous char
        processed = ''
        cursor = 0
        
        stack = []
        
        while cursor < len(text):
            c = text[cursor]
            
            # Escape macro ?
            if c == self.ESCAPE_CHAR:
                seq, cursor = self.escape(text, cursor)
                processed += seq
            
            # Macro detection (after a new line)
            elif not pc or pc == self.NL_CHAR:
                
                if text[cursor:].startswith(self.MACRO_OPEN_TAG):
                    seq, cursor = self.compile_macro(text,
                                                     cursor,
                                                     stack)
                    processed += seq
                else:
                    processed += c
            
            # Inline macro detection
            elif text[cursor:].startswith(self.IMACRO_OPEN_TAG):
                seq, cursor = self.compile_imacro(text,
                                                  cursor,
                                                  stack)
                processed += seq
            
            # Simple echo the current char
            else: processed += c
            
            pc = c
            cursor += 1
        
        return processed, stack
    
    
    def process(self, text, silent=True):
        import re
        
        def blank(*args, **kwargs):
            return ''
        
        compiled, stack = self.compile(text)
        
        processed = compiled
        cpattern = re.compile('\x0f(\d+)\x0e', re.M)
        
        for m in cpattern.finditer(compiled):
            p = int(m.group(1))
            macro_type = stack[p][0]
            funcname = stack[p][1]
            stacked = {}
            
            func = blank
            args = []
            replacement = ''
            
            if macro_type == self.MACRO_INLINE:
                stacked = self.inline_macros
            elif macro_type == self.MACRO_BLOCK:
                stacked = self.macros
            
            if not funcname in stacked:
                if not silent:
                    e = "macro %d '%s' does not exists" % (stack[p][0],
                                                           funcname)
                    raise self.MacroError(e)
            else:
                func = stacked[funcname]
                if len(stack[p]) > 2:
                    args = stack[p][2:]
            
            replacement = func(*args)
            processed = re.sub('\x0f%d\x0e' % p,
                               replacement,
                               processed)
        return processed
