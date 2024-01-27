#pip install setuptools
#pip install .

from setuptools import setup

setup(
    name='AudioBookSlides',
    version='1.0.0',
    description='Create an AI generated video slideshow from an audiobook.',
    author='Ken Selvia',
    author_email='gotaudio@gmail.com',
    url='https://github.com/GotAudio/AudioBookSlides/',
    py_modules=['abs'],
    install_requires=[
        'opencv-python',
        'openai==0.28',
        'pyyaml',
        'joblib',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'abs=abs:cli',  # Link the 'abs' command to the 'cli' function in abs.py
        ],
    },
    python_requires='>=3.6',
)
