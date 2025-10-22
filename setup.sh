#!/bin/bash

# Clinical Nutrition Platform Setup Script
echo "🏥 Setting up Clinical Nutrition Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -gt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]); then
            print_status "Python $PYTHON_VERSION found ✓"
        else
            print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if (( NODE_VERSION >= 16 )); then
            print_status "Node.js $(node --version) found ✓"
        else
            print_error "Node.js 16+ required. Found: $(node --version)"
            exit 1
        fi
    else
        print_error "Node.js not found. Please install Node.js 16+"
        exit 1
    fi
}

# Check if PostgreSQL is installed
check_postgresql() {
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL found ✓"
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL"
        print_warning "On macOS: brew install postgresql"
        print_warning "On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up Django backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cp .env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up React frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cp .env.example .env
        print_warning "Please update .env file with your Stripe keys"
    fi
    
    cd ..
}

# Create database and run migrations
setup_database() {
    print_status "Setting up database..."
    
    cd backend
    source venv/bin/activate
    
    # Create database (assumes PostgreSQL is running)
    print_status "Creating database..."
    createdb clinical_nutrition_db 2>/dev/null || print_warning "Database might already exist"
    
    # Run migrations
    print_status "Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    # Create sample data
    print_status "Creating sample data..."
    python create_sample_data.py
    
    cd ..
}

# Main setup function
main() {
    print_status "Starting Clinical Nutrition Platform setup..."
    
    # Check prerequisites
    check_python
    check_node
    check_postgresql
    
    # Setup components
    setup_backend
    setup_frontend
    setup_database
    
    print_status "Setup completed! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Update backend/.env with your database and Stripe configuration"
    echo "2. Update frontend/.env with your Stripe publishable key"
    echo "3. Start the backend: cd backend && source venv/bin/activate && python manage.py runserver"
    echo "4. Start the frontend: cd frontend && npm start"
    echo ""
    echo "Default admin credentials:"
    echo "Email: admin@example.com"
    echo "Password: admin123"
    echo ""
    echo "Sample users:"
    echo "Doctor - Email: doctor@example.com, Password: doctor123"
    echo "Patient - Email: patient@example.com, Password: patient123"
}

# Run main function
main
