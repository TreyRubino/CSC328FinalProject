# Variables
BUILD_DIR = build
EXEC_SERVER = $(BUILD_DIR)/start_server
EXEC_CLIENT = $(BUILD_DIR)/start_client

# Targets
.PHONY: all build clean

all: build

# Build executables
build: $(EXEC_SERVER) $(EXEC_CLIENT)

# Create build directory
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

# Build the server executable
$(EXEC_SERVER): server_start.py | $(BUILD_DIR)
	@echo "Creating server executable in $(BUILD_DIR)..."
	@cp $< $@
	@chmod +x $@

# Build the client executable
$(EXEC_CLIENT): client_start.py | $(BUILD_DIR)
	@echo "Creating client executable in $(BUILD_DIR)..."
	@cp $< $@
	@chmod +x $@

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@rm -rf $(BUILD_DIR)
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -exec rm -f {} +
