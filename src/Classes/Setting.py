from settings import read_settings

class Setting:
    def __init__(self, raw_dictionary, progress_bar_type, show_progress_bar, electrify_progress_bar, use_custom_progress_bar, custom_progress_bar):
        self.raw_dictionary = raw_dictionary
        self.progress_bar_type = progress_bar_type
        self.show_progress_bar = show_progress_bar
        self.electrify_progress_bar = electrify_progress_bar
        self.use_custom_progress_bar = use_custom_progress_bar
        self.custom_progress_bar = custom_progress_bar

    @staticmethod
    def new():
        settings = read_settings()
        progress_bar_type,  show_progress_bar, electrify_progress_bar, use_custom_progress_bar, custom_progress_bar = '', '', False, False, ''
        
        try:
            progress_bar_type = settings['progressBarType']
        except KeyError:
            progress_bar_type = 'default'
        
        try:
            show_progress_bar = settings['showProgressBar']
        except KeyError:
            show_progress_bar = True
       
        try:
            electrify_progress_bar = settings['electrifyProgressBar']
        except KeyError:
            electrify_progress_bar = False
       
        try:
           use_custom_progress_bar = settings['useCustomProgressBar']
        except KeyError:
            use_custom_progress_bar = False
        
        try:
           custom_progress_bar = settings['customProgressBar']
        except KeyError:
            custom_progress_bar = None

        if use_custom_progress_bar and not custom_progress_bar:
            use_custom_progress_bar = False
        
        try:
            settings['customProgressBar']['unfill_character'] = settings['customProgressBar']['unfill_character'] if not settings['customProgressBar']['unfill_character'] == '' else ' '
        except KeyError:
            pass
        return Setting(settings, progress_bar_type, show_progress_bar, electrify_progress_bar, use_custom_progress_bar, custom_progress_bar)