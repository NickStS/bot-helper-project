from setuptools import setup, find_packages

setup(
    name='bot helper',
    version='1.0.1',
    description='personal helper',
    url='http://github.com/aye4/team-bot-helper',
    author='Pythonic Coders',
    author_email='',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['bot-helper = helper.bot:bot_helper']},
)