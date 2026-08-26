from setuptools import find_packages, setup

package_name = "sentinel_autonomy"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/autonomy_tools.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Student",
    maintainer_email="student@example.com",
    description="Frontier exploration, command safety, and map health tools.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "frontier_explorer = sentinel_autonomy.frontier_explorer:main",
            "map_quality_monitor = sentinel_autonomy.map_quality_monitor:main",
            "scan_watchdog = sentinel_autonomy.scan_watchdog:main",
            "velocity_guard = sentinel_autonomy.velocity_guard:main",
        ],
    },
)

