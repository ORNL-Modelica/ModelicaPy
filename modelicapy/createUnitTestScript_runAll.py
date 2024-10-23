import re
import pathlib

class RegressionTestScriptGenerator:
    """
    This class generates a .mos simulation script for a Modelica library.
    It scans a Modelica library to find all examples, extracts experiment parameters,
    and writes corresponding simulation commands to a .mos script.
    
    Examples are identified by being in the "example_folders" and extending an "example_tags" class such as an icon.
    For example, to identify an example, place it in the "Examples" package and extend an Icon class called "Example".
    
    - To search entire library and not just a specific package/folder, set example_folder=None.
    - Multiple folders and/or tags can be searched as these are lists.
    
    library_path - path to Modelica library
    sim_env - simulation/IDE environment. Default 'dymola'
    example_folders - List of folders to search for models. Default ['Examples']. =None to search all folders.
    example_tags - List of classes that are extended to indicate it is to be simulated. Default ['Example'] (Gets converted to '.Example;')
    exclude_folders - Folders to ignore search patterns for example folders. Default ['Resources']
    """

    # The IDE specific simulation function
    SIM_FUNC_IDE = {'dymola':'simulateModel',
                     'omedit':'simulate'}
    
    # Mapping of IDE agnostic experiment parameters to mos command for simulation function
    EXP_PARAMETERS_GENERAL = {'StartTime':'startTime',
                      'StopTime':'stopTime',
                      'Interval':'outputInterval',
                      'NumberOfIntervals':'numberOfIntervals',
                      'Tolerance':'tolerance',
                      'fixedstepsize':'fixedstepsize'}
    
    # IDE specific mapping for simulation function
    EXP_PARAMETERS_IDE = {'dymola':{'Algorithm':'method'},
                           'omedit':{'s':'method'}}
    
    EXP_PARAMETERS = None # Set in set_env setter based on user sim_env
        
    def __init__(self, library_path, sim_env='dymola', example_folders=['Examples'], example_tags=['Example'], exclude_folders=['Resources']):
        self._library_path = None
        self._sim_env = None
        self._script_name = None
        self._example_folder = None
        self._example_tag = None
        self._exclude_folders = None
        
        # Setting via the property to validate.
        self.library_path = library_path
        self.sim_env = sim_env
        self.example_folders = example_folders
        self.example_tags = example_tags
        self.exclude_folders = exclude_folders

    @property
    def library_path(self) -> str:
        """Returns the library_path setting."""
        return self._library_path

    @library_path.setter
    def library_path(self, value: str) -> None:
        """
        Sets the library path. If the provided path is a directory,
        'package.mo' is appended to it.

        Args:
            value (str): The library path or a path that ends in 'package.mo'.
        """
        path = pathlib.Path(value)
        self._library_path = (path if path.name == 'package.mo' else (path / 'package.mo')).resolve()
        
    @property
    def sim_env(self) -> str:
        """Returns the sim_env setting."""
        return self._sim_env

    @sim_env.setter
    def sim_env(self, value: str) -> None:
        """Sets the sim_env."""
        self._sim_env = value.lower()
        if self._sim_env not in self.SIM_FUNC_IDE.keys():
            raise ValueError(f'Unsupported sim_env: {self._sim_env}. \n\tValid options are: {self.SIM_FUNC_IDE.keys()}')
        self._script_name = f'runAll_{self._sim_env}.mos'
        self.EXP_PARAMETERS = self.EXP_PARAMETERS_GENERAL | self.EXP_PARAMETERS_IDE[self._sim_env]
      
    @property
    def example_folders(self) -> list:
        """Returns the example_folders setting."""
        return self._example_folders

    @example_folders.setter
    def example_folders(self, value: list) -> None:
        """Sets the example_folder."""
        self._example_folders = ['*'] if value is None else value
        
    @property
    def example_tags(self) -> list:
        """Returns the example_tags setting."""
        return self._example_tags

    @example_tags.setter
    def example_tags(self, value: list) -> None:
        """Sets the example_tags."""
        self._example_tags = value
        
    @property
    def exclude_folders(self) -> list:
        """Returns the exclude_folders setting."""
        return self._exclude_folders

    @exclude_folders.setter
    def exclude_folders(self, value: list) -> None:
        """Sets the exclude_folders."""
        self._exclude_folders = set([]) if value is None else set(value)
            
    def _find_exp_setting(self, line, lines, num, setting_dict):
        """
        Extract experiment settings from a set of lines based on a given dictionary of settings.
        
        This function processes a set of lines from a file, extracts key-value pairs,
        and matches them against a provided dictionary of experiment settings.
        """
        exp_list = {}
        line_list = re.findall(r'[^,;()]+', ''.join(line.rstrip('\n').strip() for line in lines[num - 1:]))
        line_list = [item for item in line_list if '=' in item] # Remove all items in list that don't have an equal sign
        if self.sim_env == 'dymola':
            line_list = [s.replace('__Dymola_', '').replace(' ', '') for s in line_list]
            
        # Convert the values to dictionary pairs
        list_dict = {item.split('=')[0].strip(' '): item.split('=')[1] for item in line_list if '=' in item}
        list_dict
        for exp_key, exp_value in setting_dict.items():
            for key, value in list_dict.items():
                if exp_key == key:
                    exp_list[exp_value] = value
                    break
        return exp_list
    
    def generate_test_list(self):
        """
        Walks through the Modelica library to find all .mo files that are in 
        the example_folder and contain the example_tag.
        
        Returns:
            list: A list of pathlib.Path objects for the found test files.
        """
        directory_list = []
        
        # Walk through the directory tree
        for folder in self._example_folders:
            for path in self.library_path.parent.rglob(folder):
                if not any(excl in path.parts for excl in self._exclude_folders):
                    directory_list.append(path)

        test_list = []
        for example_dir in directory_list:
            for mo_file in example_dir.rglob('*.mo'):
                with mo_file.open('r') as fil:
                    for line in fil:
                        if any(f'.{tag};' in line for tag in self._example_tags):
                            test_list.append(mo_file)
                            break
        

        # Remove duplicates while retaining order (can occur when exampled_folders=None)
        seen = set()
        unique_test_list = [x for x in test_list if not (x in seen or seen.add(x))]
        
        return unique_test_list
        
    def generate_mos_script(self, test_list, output_path=None):
        """
         Generates a .mos file containing simulation commands for all tests.
         
         Args:
             test_list (list): List of test file paths generated from `generate_test_list`.
         """
        if output_path is None:
            output_path = self.library_path.parent
        else:
            output_path = pathlib.Path(output_path)
    
        run_all_path = output_path / f'runAll_{self.sim_env}.mos'
        if run_all_path.exists():
            run_all_path.unlink()  # Remove the existing file
    
        for item in test_list:
            with open(item, 'r') as fil:
                lines = fil.readlines()

            exp_list = {}
            with open(item, 'r') as fil:
                for num, line in enumerate(fil, 1):
                    temp = {}
                    if 'experiment(' in line:
                        settings_dict = self.EXP_PARAMETERS_GENERAL | (self.EXP_PARAMETERS_IDE[self.sim_env] if self.sim_env == 'dymola' else {})
                        temp = self._find_exp_setting(line, lines, num, settings_dict)

                    if '__OpenModelica_simulationFlags' in line and self.sim_env == 'omedit':
                        temp = self._find_exp_setting(line, lines, num, self.EXP_PARAMETERS_IDE[self.sim_env])
                    exp_list = exp_list | temp
      
            model_name = pathlib.Path(item).stem
            model_sim_path = ''.join(re.findall(r'[^;]+', lines[0].rstrip('\n')))
            model_sim_path = re.sub('.*within', '', model_sim_path).replace(' ', '')
            plot_sim_path = f'{model_sim_path}.{model_name}'

            with run_all_path.open('a') as mos_dym:
                mos_dym.write(f'{self.SIM_FUNC_IDE[self._sim_env]}("{plot_sim_path}",')
                for key, value in exp_list.items():
                    mos_dym.write(f'{key}={value},')
                mos_dym.write(f'resultFile="{model_name}");\n')


    def run(self, output_path=None):
        """
        Main execution method that generates the test list and the .mos script.
        
        output_path - path to place the runAll_*.mos file. Default is None (i.e., location of library_path)
        """
        test_list = self.generate_test_list()
        self.generate_mos_script(test_list, output_path)
        
def find_failed_tests(filename, sim_env='dymola'):
    '''
    Function that takes the location of the simulation output from running runAll_*.mos 
    and returns a list of the models which failed the "simulateModel" command.
    
    filename - copy and past the contents of the simulation command log (or save to a file)
    '''
    if sim_env == 'dymola':
        def extract_between_quotes(input_string):
            match = re.search(r'"(.*?)"', input_string)
            if match:
                return match.group(1)
            return None
        
        with open(filename, 'r') as fil:
            lines = fil.readlines()
            
        result = []
        for i, line in enumerate(lines):
            if 'simulateModel(' in line:
                model = extract_between_quotes(line)
                temp = lines[i+1]
                temp = temp.replace(' ','').replace('=','').strip()
                temp = True if temp == 'true' else False
                result.append((model, temp))

    failed = []
    for tup in result:
        if not tup[1]:
            failed.append(tup[0])
    return failed
   
class RunAllLogProcessor:
    '''
    Class that takes the location of the simulation output from running runAll_*.mos 
    and returns a list of the models which failed the "simulateModel" command.
    
    filenames - list of copy and paste the contents of the simulation command log to a text file (or save to a file)
    '''
    
    def __init__(self, filenames):
        self.filenames = filenames
        self.results = []
        self.failed_models = []
        self.sim_env = 'dymola'
        
    def extract_between_quotes(self, input_string):
        match = re.search(r'"(.*?)"', input_string)
        if match:
            return match.group(1)
        return None

    def get_result(self, lines):
        result = []
        if self.sim_env == 'dymola':
            for i, line in enumerate(lines):
                if 'simulateModel(' in line:
                    model = self.extract_between_quotes(line)
                    temp = lines[i + 1].replace(' ', '').replace('=', '').strip()
                    temp = True if temp == 'true' else False
                    result.append((model, temp))
            return result
        else:
            raise ValueError('Unsupported sim_env')
            
    def get_failed(self, result):
        return [model for model, passed in result if not passed]

    def process_file(self, filename):
        with open(filename, 'r') as fil:
            lines = fil.readlines()
        result = self.get_result(lines)
        self.results.append(result)
        failed = self.get_failed(result)
        self.failed_models.append(failed)

    def process_all_files(self):
        for filename in self.filenames:
            self.process_file(filename)

    def unique_failed_items(self):
        if len(self.failed_models) < 2:
            return [], []  # Not enough data for comparison
        set1, set2 = set(self.failed_models[0]), set(self.failed_models[1])
        return list(set1 - set2), list(set2 - set1)
    
if __name__ == "__main__":
    # Path to the Modelica library.
    library_path = r'E:\Modelica\TRANSFORM-Library\TRANSFORM'

    # Initialize the generator and execute the script generation process.
    generator = RegressionTestScriptGenerator(library_path)
    generator.run()


    #%% Runall (only works if you have valid filenames)
    filenames = [r'resources/log_0.txt', r'resources/log_1.txt']
    processor = RunAllLogProcessor(filenames)
    processor.process_all_files()

    unique_1, unique_2 = processor.unique_failed_items()
    print("Unique to file 1:", unique_1)
    print("Unique to file 2:", unique_2)
    