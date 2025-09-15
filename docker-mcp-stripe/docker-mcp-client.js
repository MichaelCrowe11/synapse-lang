/**
 * Docker MCP Client for Claude Desktop Integration
 * Connects to the Synapse Stripe MCP server and provides tools for Claude
 */

const WebSocket = require('ws');
const { EventEmitter } = require('events');

class DockerMCPClient extends EventEmitter {
  constructor(serverUrl = 'ws://localhost:3002/mcp') {
    super();
    this.serverUrl = serverUrl;
    this.ws = null;
    this.connected = false;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.availableTools = [];
  }

  // Connect to MCP server
  async connect() {
    return new Promise((resolve, reject) => {
      console.log(`🔗 Connecting to MCP server at ${this.serverUrl}`);
      
      this.ws = new WebSocket(this.serverUrl);
      
      this.ws.on('open', () => {
        console.log('✅ Connected to MCP server');
        this.connected = true;
        this.emit('connected');
        resolve();
      });

      this.ws.on('message', (data) => {
        this.handleMessage(data);
      });

      this.ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
        reject(error);
      });

      this.ws.on('close', () => {
        console.log('🔌 Disconnected from MCP server');
        this.connected = false;
        this.emit('disconnected');
      });
    });
  }

  // Handle incoming messages
  handleMessage(data) {
    try {
      const message = JSON.parse(data.toString());
      
      // Handle initialization message
      if (message.method === 'initialize') {
        this.availableTools = message.params?.capabilities?.tools || [];
        console.log(`🛠️  Available tools: ${this.availableTools.length}`);
        this.availableTools.forEach(tool => {
          console.log(`   - ${tool.name}: ${tool.description}`);
        });
        return;
      }

      // Handle response to our request
      if (message.id && this.pendingRequests.has(message.id)) {
        const { resolve, reject } = this.pendingRequests.get(message.id);
        this.pendingRequests.delete(message.id);
        
        if (message.error) {
          reject(new Error(message.error.message));
        } else {
          resolve(message.result);
        }
      }
    } catch (error) {
      console.error('❌ Error parsing message:', error);
    }
  }

  // Send request to MCP server
  async sendRequest(method, params = {}) {
    if (!this.connected) {
      throw new Error('Not connected to MCP server');
    }

    const id = ++this.requestId;
    const request = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      
      // Set timeout for request
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);

      this.ws.send(JSON.stringify(request));
    });
  }

  // Stripe tool wrappers for Claude Desktop
  async createCustomer(email, name, metadata = {}) {
    console.log(`👤 Creating Stripe customer: ${email}`);
    return await this.sendRequest('stripe-create-customer', {
      email,
      name,
      metadata
    });
  }

  async createSubscription(customerId, priceId, paymentMethodId = null) {
    console.log(`💳 Creating subscription for customer: ${customerId}`);
    return await this.sendRequest('stripe-create-subscription', {
      customerId,
      priceId,
      paymentMethodId
    });
  }

  async createCheckoutSession(customerId, priceId, successUrl, cancelUrl) {
    console.log(`🛒 Creating checkout session for: ${customerId}`);
    return await this.sendRequest('stripe-create-checkout', {
      customerId,
      priceId,
      successUrl,
      cancelUrl
    });
  }

  async cancelSubscription(subscriptionId, cancelAtPeriodEnd = true) {
    console.log(`❌ Canceling subscription: ${subscriptionId}`);
    return await this.sendRequest('stripe-cancel-subscription', {
      subscriptionId,
      cancelAtPeriodEnd
    });
  }

  async getCustomer(customerId) {
    console.log(`🔍 Getting customer details: ${customerId}`);
    return await this.sendRequest('stripe-get-customer', {
      customerId
    });
  }

  async listSubscriptions(customerId, limit = 10) {
    console.log(`📋 Listing subscriptions for: ${customerId}`);
    return await this.sendRequest('stripe-list-subscriptions', {
      customerId,
      limit
    });
  }

  async createPortalSession(customerId, returnUrl) {
    console.log(`🏪 Creating portal session for: ${customerId}`);
    return await this.sendRequest('stripe-create-portal', {
      customerId,
      returnUrl
    });
  }

  // Disconnect from server
  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  // Get available tools
  getAvailableTools() {
    return this.availableTools;
  }

  // Check connection status
  isConnected() {
    return this.connected;
  }
}

// Export for use in Claude Desktop
module.exports = DockerMCPClient;

// Demo usage if run directly
if (require.main === module) {
  async function demo() {
    const client = new DockerMCPClient();
    
    try {
      await client.connect();
      
      // Wait for initialization
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('🧪 Running demo operations...');
      
      // Test creating a customer
      const customerResult = await client.createCustomer(
        'demo@synapse.com',
        'Demo User',
        { source: 'mcp-demo' }
      );
      
      console.log('✅ Customer created:', customerResult);
      
      if (customerResult.success) {
        const customerId = customerResult.customer.id;
        
        // Test creating checkout session
        const checkoutResult = await client.createCheckoutSession(
          customerId,
          'price_1S6U8fQ6s74Bq3bW9I2Ff3qW', // Starter monthly
          'http://localhost:3000/success',
          'http://localhost:3000/cancel'
        );
        
        console.log('✅ Checkout session:', checkoutResult);
      }
      
    } catch (error) {
      console.error('❌ Demo error:', error);
    } finally {
      client.disconnect();
    }
  }
  
  demo();
}