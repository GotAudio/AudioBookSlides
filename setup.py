#pip install setuptools
#pip install .

from setuptools import setup, find_packages

setup(
    name='AudioBookSlides',
    version='1.0.0',
    description='Create an AI generated video slideshow from an audiobook.',
    author='Ken Selvia',
    author_email='gotaudio@gmail.com',
    url='https://github.com/GotAudio/AudioBookSlides/',
    packages=find_packages(),
    install_requires=[
        'opencv-python',  # This is the package name for cv2
        'openai==0.28',
        'pyyaml',         # This is the package name for yaml
        'joblib',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'audioslides=abs:main',  # 'audioslides' is the command, 'abs:main' means the main function in 'abs.py'
        ],
    },
    python_requires='>=3.6',  # Specify your required Python version
    # include_package_data=True,
    # package_data={
    #     # If there are data files included in your packages
    #     'package_name': ['data/*.dat'],
    # },
    # scripts=['scripts/some_script.py'],
)
