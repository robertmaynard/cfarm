#How to setup machine to use cfarm#

#OSX#

First we need to setup a stable python platform for python, this means
getting pip the python package manager, and virtual env which isolates
projects python libraries.

```
sudo install pip
sudo install virtualenv
```

Next we need to create a new virtual env of python for cfarm. I personally
like to setup in my cfarm source directory a folder call env. This will hold
the python libraries for cfarm. By the way, cfarm natually has the env folder in
the source directory part of its .gitignore so don't worry about accidentally
committing your env to the git repo.

```
mkdir env
virtualenv env
````

Now we have virtual env folder setup!

Now all we have to do is setup the requirements for cfarm, which is super
easy since we are using pip. Pip provides the ability to install all the
requirements of a project ( http://www.pip-installer.org/en/latest/cookbook.html#requirements-files ).
So lets go install cfarm's requirements.


```
env/bin/pip -r requirements.txt
```

And now your virtualenv has all of cfarm requirements and you can start
developing!
