from setuptools import setup, find_packages

# Load README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    

setup(
    name="ptrl",
    version="0.0.1",
    author="Sofiene Lassoued",
    author_email="lassoued.sofiene@fh-swf.de",
    description="PTRL: Petri Nets Reinforcement Learning for discrete event systems",
    long_description=long_description ,
    long_description_content_type="text/markdown",
    install_requires=["gymnasium", "pandas", "numpy"],
    packages=find_packages(),
   

package_data={
    'ptrl': [
        'envs/*',
        'render/*',    
        'utils/*', 
        'fms_agv/*',
        'common/*',
        'common/instances/Taillard/*',
        'common/instances/BU/*',
        'common/instances/Demirkol/*',
    ] ,
         
    },
    url="https://www.fh-swf.de/de/forschung___transfer_4/labore_3/labs/labor_fuer_automatisierungstechnik__soest_1/standardseite_57.php",
    project_urls={
        "Documentation": "https://arxiv.org/abs/2402.00046",
        "Repository": "https://github.com/Sofiene-Uni/ptrl"
    },
)