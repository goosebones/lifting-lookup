

Here's the revised step-by-step guide using AWS web interface and Git:

### 1. Prepare Your Application Files
Create these additional files in your project:

```text:requirements.txt
flask
flask-cors
flask-caching
boto3
python-dotenv
gunicorn
```

```text:wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

Push your code to a Git repository (GitHub, GitLab, etc.).

### 2. Launch EC2 Instance
1. Go to AWS Console → EC2 Dashboard
2. Click "Launch Instance"
3. Configure your instance:
   - Choose "Ubuntu Server 22.04 LTS" as the AMI
   - Select t2.micro (free tier) or larger instance type
   - Configure Security Group:
     - Allow HTTP (Port 80) from anywhere
     - Allow HTTPS (Port 443) from anywhere
     - Allow Custom TCP (Port 5000) from anywhere (for development)
4. Launch the instance

### 3. Connect to Your EC2 Instance
1. Select your instance in EC2 Dashboard
2. Click "Connect"
3. Choose "EC2 Instance Connect"
4. Click "Connect"

### 4. Set Up the Server
Run these commands in the EC2 Instance Connect terminal:

```bash
# Update package manager
sudo apt update
sudo apt upgrade -y

# Install Python, Git and required tools
sudo apt install -y python3-pip python3-venv nginx git

# Create a directory for your application
mkdir ~/lifting-lookup
cd ~/lifting-lookup

# Clone your repository
git clone <<your-repository-url>> .

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Set Up Gunicorn
```bash
# Test Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:app

# Create a systemd service file
sudo nano /etc/systemd/system/lifting-lookup.service
```

```text:/etc/systemd/system/lifting-lookup.service
[Unit]
Description=Gunicorn instance to serve lifting-lookup
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/lifting-lookup
Environment="PATH=/home/ubuntu/lifting-lookup/.venv/bin"
ExecStart=/home/ubuntu/lifting-lookup/.venv/bin/gunicorn --workers 3 --bind unix:lifting-lookup.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

### 6. Configure Nginx
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/lifting-lookup
```

```text:/etc/nginx/sites-available/lifting-lookup
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/lifting-lookup/lifting-lookup.sock;
    }
}
```

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/lifting-lookup /etc/nginx/sites-enabled

# Test Nginx configuration
sudo nginx -t

# Remove default Nginx configuration (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### 7. Start Services
```bash
# Start and enable Gunicorn service
sudo systemctl start lifting-lookup
sudo systemctl enable lifting-lookup

# Restart Nginx
sudo systemctl restart nginx
```

### 8. Set Up Environment Variables
```bash
# Create .env file
nano .env
# Add your environment variables here
```

### 9. Monitor Logs
```bash
# View application logs
sudo journalctl -u lifting-lookup.service

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### To Update Your Application
When you need to update your application:
```bash
# Go to your application directory
cd ~/lifting-lookup

# Pull latest changes
git pull

# Restart the service
sudo systemctl restart lifting-lookup
```

### Important Notes:
1. Replace `your-repository-url` with your actual Git repository URL
2. Replace `your_domain_or_ip` in the Nginx configuration with your EC2 instance's public IP or domain
3. Make sure your `.env` file contains all necessary environment variables
4. If your repository is private, you'll need to:
   - Set up Git credentials on the EC2 instance
   - Or use a personal access token
   - Or use SSH keys for Git

### Security Considerations:
1. Set up proper IAM roles for EC2 to access DynamoDB
2. Configure SSL/TLS with Let's Encrypt
3. Set up proper firewall rules
4. Consider using AWS Secrets Manager for environment variables
5. Don't commit sensitive information to your Git repository

### Troubleshooting:
- Check service status: `sudo systemctl status lifting-lookup`
- Check Nginx status: `sudo systemctl status nginx`
- Check application logs: `sudo journalctl -u lifting-lookup.service`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- If you make changes to the service file: 
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart lifting-lookup
  ```