"""These are not the modules you're looking for.

This module in particular is not normal. Do not import it if you wish to remain normal.

It dynamically loads the required personality from the environment and patches the python
import machinery to prevent loading any other personalities by the auxiliary config setup
in _local.py.
"""
import os
from typing import TYPE_CHECKING, Iterable, Tuple

if TYPE_CHECKING:
	import pathlib


def _iter_personality_modules() -> Iterable['pathlib.Path']:
	import pathlib

	for mdl in pathlib.Path(__file__).parent.iterdir():
		if not mdl.is_file() or any(map(mdl.name.startswith, ('.', '_'))) or mdl.suffix != '.py':
			continue
		# Some whitelisted files are not personalities per se, just supporting
		# modules that aren't immediately imported by other configs.
		if mdl.stem in ('dynamic', 'test'):
			continue
		yield mdl


def _decorate_xformed_module_path(paths: Iterable['pathlib.Path']) -> Iterable[Tuple['pathlib.Path', str]]:
	base_package_path, _, _ = __name__.rpartition('.')
	for mdl in paths:
		yield mdl, f'{base_package_path}.{mdl.stem}'


def _fake_secrets(postgres):
	import sys
	import types

	# Synthesize secrets module.
	secrets_name = 'ui.config.settings.secrets.secrets'
	secrets = types.ModuleType(secrets_name)
	secrets.SECRET_KEY = 'itteh bitteh sekrit committeh'
	secrets.DATABASE_NAME = 'putka5'
	secrets.RECAPTCHA_PRIVATE_KEY = ''
	secrets.RECAPTCHA_PUBLIC_KEY = ''
	secrets.EMAIL_HOST = ''
	secrets.EMAIL_HOST_USER = ''
	secrets.EMAIL_HOST_PASSWORD = ''
	secrets.EMAIL_PORT = 0
	secrets.EMAIL_USE_TLS = True
	secrets.DATABASE_USER = 'putka' if postgres else ''
	secrets.DATABASE_PASSWORD = ''
	sys.modules[secrets_name] = secrets


# Do everything in a function, so it doesn't pollute the global namespace.
def _load(postgres):
	import importlib
	import pathlib
	import sys

	_fake_secrets(postgres)

	# Import the target personality module.
	target_personality = os.environ['PUTKA_PERSONALITY']
	base_package_path, _, _ = __name__.rpartition('.')
	personality_module_name = f'{base_package_path}.{target_personality}'
	personality_module = importlib.import_module(personality_module_name)

	# Patch all other personality modules into existence without importing,
	# all linking to the same physical module. This will effectively override
	# the "from .personality import *" statement in _local.py.
	for _, mdl_name in _decorate_xformed_module_path(_iter_personality_modules()):
		if mdl_name not in sys.modules:
			sys.modules[mdl_name] = personality_module


def _load_specific_db(name):
	# Load a specific config module temporarily, get its database config, then delete it.
	import importlib
	import sys

	prior_modules = set(sys.modules.keys())
	module = importlib.import_module(name)
	for m in set(sys.modules.keys()) - prior_modules:
		del sys.modules[m]

	return module.DATABASES


# if os.environ['PUTKA_PERSONALITY'] == 'mypy' or TYPE_CHECKING:
# 	# Import everything we have so that the mypy and the Django mypy plugin
# 	# can typecheck all our settings. The problem is that mypy doesn't actually
# 	# execute any of the files it typechecks, so e.g. the following (left for posterity
# 	# and in case anything changes) does not work:
# 	#
# 	# 	import importlib
# 	# 	for _, mdl_name in _decorate_xformed_module_path(_iter_personality_modules()):
# 	# 		mdl = importlib.import_module(mdl_name)
# 	# 		if hasattr(mdl, '__all__'):
# 	# 			mdl_all = mdl.__all__
# 	# 		else:
# 	# 			mdl_all = [x for x in mdl.__dict__ if not x.startswith("_")]
# 	# 		globals().update({n: getattr(mdl, n) for n in mdl_all})
# 	#
# 	# So import everything in a pedestrian way (which is also good enough for the plugin).
# 	# Sanity checks aren't really possible this way tho.
# 	# Same order as declared in .ci/runner.sh
# 	_fake_secrets(False)
# 	from .ceoi import *
# 	from .cerc import *
# 	from .classic import *
# 	from .rtk import *
# 	from .tomo import *
# 	from .upm import *
# else:
# 	_db_config = None
# 	if os.environ.get('PUTKA_TESTING_DB_OVERRIDE', 'nope').startswith('ui.config.'):
# 		# This has to be done first, because _load() will override
# 		# all modules later.
# 		_db_config = _load_specific_db(os.environ['PUTKA_TESTING_DB_OVERRIDE'])
# 		if 'PORT' in _db_config['default'].get('TEST', {}):
# 			# The PORT setting can't be overridden in the TEST dictionary.
# 			_db_config['default']['PORT'] = _db_config['default']['TEST']['PORT']

# 	_load(os.environ.get('PUTKA_TESTING_DB_OVERRIDE', 'nope') == 'postgres')

# 	from ._local import *

# 	if os.environ.get('PUTKA_TESTING_FULL', None) == 'true':
# 		if os.environ.get('PUTKA_TESTING_DB_OVERRIDE', None) != 'postgres':
# 			DATABASES['default']['TEST'] = FULL_TESTING_DB
# 		if 'PUTKA_TEST_RUNLOOPS' in os.environ:
# 			# They fork+exec over there, so any settings overrides would get lost.
# 			if os.environ['PUTKA_TEST_RUNLOOPS'].endswith('runloops_localmetrics.txt'):
# 				LOCALMETRICS_BACKEND = 'ui.core.common.test_sys_lifecycle.InspectorBackend'
# 			elif os.environ['PUTKA_TEST_RUNLOOPS'].endswith('runloops_forced_new.txt'):
# 				LOCALMETRICS_BACKEND = 'ui.core.common.test_sys_lifecycle.AggressiveRunloopStarterBackend'
# 		FULL_TESTING = True

# 	if _db_config is not None:
# 		DATABASES = _db_config

# 	# Test-related overrides.
# 	LANGUAGE_CODE = 'en'
# 	LANGUAGES = (
# 		('sl', 'Slovenian'),
# 		('en', 'English'),
# 	)
# 	STORAGES['staticfiles']['BACKEND'] = 'django.contrib.staticfiles.storage.StaticFilesStorage'
