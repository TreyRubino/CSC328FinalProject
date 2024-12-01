# Variables
BUILD_DIR = build
EXEC_SERVER = $(BUILD_DIR)/fileserver
EXEC_CLIENT = $(BUILD_DIR)/fileclient

# Targets
.PHONY: all build clean

all: build $(EXEC_SERVER) $(EXEC_CLIENT)

# Create build directory
build:
	@mkdir -p $(BUILD_DIR)

# Build the server executable
$(EXEC_SERVER): src/start_server.py | $(BUILD_DIR)
	@echo "Creating server executable in $(BUILD_DIR)..."
	@cp $< $@
	@chmod +x $@

# Build the client executable
$(EXEC_CLIENT): src/start_client.py | $(BUILD_DIR)
	@echo "Creating client executable in $(BUILD_DIR)..."
	@cp $< $@
	@chmod +x $@

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@rm -rf $(BUILD_DIR)
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -exec rm -f {} +
