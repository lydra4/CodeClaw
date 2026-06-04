#!/bin/bash

set -e

echo "🚀 Starting CodeClaw WSL Environment Setup..."

echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo "🟢 Installing Node.js v24..."
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "🍺 Installing Homebrew..."
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo "🔗 Configuring Homebrew PATH..."
if ! grep -q 'linuxbrew' ~/.bashrc; then
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
fi
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

echo "🤖 Installing OpenClaw..."
sudo npm install -g openclaw

echo "📁 Setting up configuration directories..."
mkdir -p config
touch config/.env
echo "config/.env" >> .gitignore

echo "✅ Base installation complete!"
echo "⚠️ IMPORTANT NEXT STEP: OpenClaw's setup wizard is highly interactive."
echo "Please run 'openclaw doctor' manually to complete the UI configuration."
