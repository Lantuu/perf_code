

class CommitData:

    _file_path = ''
    _project_name = ''
    _line_no = -1
    _commit_id = ''
    _evol_type = ''
    _desc = ''
    _sig = []
    _id = -1

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        if not isinstance(file_path, str):
            raise ValueError('score must be a String')
        self._file_path = file_path

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        if not isinstance(project_name, str):
            raise ValueError('score must be a String')
        self._project_name = project_name

    @property
    def line_no(self):
        return self._line_no

    @line_no.setter
    def line_no(self, line_no):
        if not isinstance(line_no, int):
            raise ValueError('score must be a Integer')
        self._line_no = line_no

    @property
    def commit_id(self):
        return self._commit_id

    @commit_id.setter
    def commit_id(self, commit_id):
        if not isinstance(commit_id, str):
            raise ValueError('score must be a String')
        self._commit_id = commit_id

    @property
    def evol_type(self):
        return self._evol_type

    @evol_type.setter
    def evol_type(self, evol_type):
        if not isinstance(evol_type, str):
            raise ValueError('score must be a String')
        self._evol_type = evol_type

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, desc):
        if not isinstance(desc, str):
            raise ValueError('score must be a String')
        self._desc = desc

    @property
    def sig(self):
        return self._sig

    @sig.setter
    def sig(self, sig):
        if not isinstance(sig, list):
            raise ValueError('score must be a List')
        self._sig = sig

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        if not isinstance(id, int):
            raise ValueError('score must be a Integer')
        self._id = id

    def get_dic(self):
        desc = self.desc
        if self.desc.startswith('-'):
            desc = ' ' + desc
        return({'id': self.id,
                'path': self.file_path,
                'commit_id': self.commit_id,
                'type': self.evol_type,
                'project': self.project_name,
                'line_no': self.line_no,
                'sig': self.sig,
                'desc': desc})

    def print_data(self):
        print("path: '"+self._file_path+"', project: '"+self._project_name+"', lineno: "+str(self._line_no)+", commit_id: '"
              + self._commit_id+"', type: '"+self._evol_type+"', desc: '"+self. _desc+"', sig: '"+str(self. _sig))


