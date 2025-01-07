set -x

cd /workspace

git clone 'https://github.com/eoap/mastering-app-package.git'

code-server --install-extension ms-python.python
code-server --install-extension redhat.vscode-yaml
code-server --install-extension sbg-rabix.benten-cwl
code-server --install-extension ms-toolsai.jupyter

ln -s /workspace/.local/share/code-server/extensions /workspace/extensions

exit 0
