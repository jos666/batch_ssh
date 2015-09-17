import os


class complte_dir(object):
    def complte_dir(self, dirname):
        if os.path.isdir(dirname) and os.path.exists(dirname):
            return os.listdir(dirname)
        else:
            num = [n for n in xrange(len(dirname)) if dirname[n] == '/'].pop()
            return os.listdir(dirname[:num if num > 0 else 1])

    def complte(self, txt):
        txt = txt if txt else "/"
        num = [n for n in xrange(len(txt)) if txt[n] == '/']
        num = num.pop() if num else 0
        match_txt = txt[num + 1:]
        dirfiles = self.complte_dir(txt)
        if txt[-1:] != "/" and os.path.isdir(txt):
            return [match_txt + '/']
        files = [f for f in dirfiles if f.startswith(match_txt)]
        return files

if __name__ == '__main__':
    print complte_dir().complte("/usr/")
