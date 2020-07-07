class ConfigNotFoundError(Exception):
	"""
	ConfigNotFoundError: Error if config is not found
 	"""
	def __init__(self, config):
		"""
		__init__

		Args:
			config ([str]): takes in name of config that is not found.
		"""
		self.config = config
		self.message = message=f"Config {self.config} is not found!"
		super().__init__(self.message)