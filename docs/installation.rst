Setting up JupyterLab
=====================

Every JupyterLab is seperated from each other and deployed on it's own Docker container.
This means Versions, especially the JupyterLab version can differ between different instances which is depending on 
the point in time of creation of the docker-image.




Docker
------

For the deployment of and docker container, an docker-image is required. Therefore a the ** INSERT PACKAGE **
package is delivered.

This package contains all requirements including ``libGInsUtility.so`` to be able to run all current python scripts on an ``Gantner cloud tenant``
Furthermore the building the image will always pull the latest available version of Jupyter.

To build an image simply run:

.. code-block:: bash
	
	$ docker build -t JupyterLab_image .


.. note::

	For deployment a specific Gantner docker-compose.yml file is being used.


Compatability
-------------

Note that you can build and run this docker-container on every linux-based machine.


For local testing purposes a simple docker-compose.yml file is delivered, which can simply be run with:

.. code-block:: bash
	
	$ docker-compose up

.. warning::

	Python scripts writing to the Gantner backend utilizing **libGInsUtility** will not work outside the GI.Cloud cluster.



libGInsUtility
--------------

The GInsData API provides a unified platform independant interface to measurement data from controllers like e.gate/pac, Q.gate/pac or Q.station and ProcessBuffers of GI.data (GI.bench). 
No 3rd-party libraries required, stdc++ library statically linked to reduce platform/version dependencies. 
The Gantner Library is called „giutility.dll“ (Windows) or „libGInsUtility.so“ (Linux).

For detailed explanation and Python examples view the GInsUtility_Documentation_ for further information.

.. _GInsUtility_Documentation: https://dev.gantner-instruments.com/webfiles/public/Download/Software/Python/ginsapy/doc/build/html/index.html

.. important:: When developing with this library please refer to the  ::download:`C-Headerfile <\eGateHighSpeedPort.h>` to get have documentation of implemented functions.




