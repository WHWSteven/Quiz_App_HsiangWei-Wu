const express = require('express');
const axios = require('axios');
const jwt = require('jsonwebtoken');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cookieParser = require('cookie-parser');

const app = express();

// JWT secret - should be in environment variable in production
const JWT_SECRET = 'your-secret-key-change-in-production';
const USER_SERVICE_URL = 'http://localhost:5001';
const QUIZ_SERVICE_URL = 'http://localhost:5000';
const SAGA_ORCHESTRATOR_URL = 'http://localhost:5002';

// CORS middleware - allow requests from Flask app with credentials
// CRITICAL: Cannot use '*' with credentials: true - must specify exact origin
const ALLOWED_ORIGINS = ['http://127.0.0.1:5000', 'http://localhost:5000'];

app.use((req, res, next) => {
  const origin = req.headers.origin;
  
  // Check if origin is in allowed list
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
  } else if (origin) {
    // For development, allow any localhost/127.0.0.1 origin
    if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
      res.header('Access-Control-Allow-Origin', origin);
    }
  }
  
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-User-Id');
  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Access-Control-Expose-Headers', 'Set-Cookie');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Middleware to parse cookies (needed for JWT in cookies)
app.use(cookieParser());

// Only parse body for /auth routes - don't parse for proxy routes
// This allows form data to pass through to Flask correctly
app.use('/auth', express.json());
app.use('/auth', express.urlencoded({ extended: true }));

// For non-auth routes, don't parse body at all - proxy will handle streaming

// Custom login endpoint
app.post('/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    // Validate credentials with User Service
    const response = await axios.post(`${USER_SERVICE_URL}/users/validate`, {
      username,
      password
    });

    if (response.status === 200) {
      const user = response.data;
      
      // Sign JWT with user info
      const token = jwt.sign(
        { 
          sub: user.id.toString(),
          userId: user.id,
          username: user.username 
        },
        JWT_SECRET,
        { expiresIn: '24h' }
      );

      // Set token in cookie for navigation
      // CRITICAL: Set cookie with proper settings for cross-origin requests
      res.cookie('authToken', token, { 
        httpOnly: false, 
        maxAge: 24 * 60 * 60 * 1000,
        path: '/',
        sameSite: 'lax'  // Allow cookie to be sent with cross-site requests
      });
      
      // Migrate guest quiz results to user account (if any exist)
      // This ensures guest results created before login are preserved
      try {
        // Get session cookie from request to identify guest session
        const sessionCookie = req.cookies && req.cookies.session ? req.cookies.session : null;
        
        // Call migration endpoint to migrate guest results
        // Note: The Quiz Service will get the session_id from Flask session
        const migrateResponse = await axios.post(
          `${QUIZ_SERVICE_URL}/migrate-guest-results`,
          {},
          {
            headers: {
              'X-User-Id': user.id.toString(),
              'Cookie': req.headers.cookie || '' // Forward cookies so Flask can get session_id
            }
          }
        );
        
        if (migrateResponse.data.migrated > 0) {
          console.log(`Migrated ${migrateResponse.data.migrated} guest quiz results to user ${user.id}`);
        }
      } catch (migrateError) {
        // Migration failure is non-critical - log but don't fail login
        console.log('Guest result migration failed (non-critical):', migrateError.message);
      }
      
      return res.json({ token });
    }
  } catch (error) {
    if (error.response) {
      // Forward error from User Service
      const status = error.response.status;
      const errorData = error.response.data || { error: 'Invalid credentials' };
      return res.status(status).json(errorData);
    }
    console.error('Login error:', error.message);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Custom register endpoint - Uses Saga Orchestrator
app.post('/auth/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }

    // Trigger Registration Saga via Saga Orchestrator
    console.log('Triggering Registration Saga via Orchestrator...');
    const sagaResponse = await axios.post(`${SAGA_ORCHESTRATOR_URL}/saga/register`, {
      username,
      email,
      password
    });

    if (sagaResponse.status !== 202) {
      return res.status(500).json({ error: 'Failed to trigger registration saga' });
    }

    const { saga_id, task_id } = sagaResponse.data;
    console.log(`Saga started: ${saga_id}, Task ID: ${task_id}`);

    // Poll for saga completion (with timeout)
    const maxAttempts = 30; // 30 attempts
    const pollInterval = 1000; // 1 second
    let attempts = 0;

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, pollInterval));
      
      try {
        const statusResponse = await axios.get(`${SAGA_ORCHESTRATOR_URL}/saga/status/${task_id}`);
        const { status, result, error } = statusResponse.data;

        if (status === 'SUCCESS') {
          // Saga completed successfully
          // The saga returns: { success: true, saga_id: ..., result: { user: ..., profile: ... } }
          const sagaResult = result?.result || result;
          const user = sagaResult?.user;
          
          if (!user) {
            console.error('Saga result structure:', JSON.stringify(result, null, 2));
            return res.status(500).json({ 
              error: 'Saga completed but no user data returned',
              debug: { result, sagaResult }
            });
          }

          // Sign JWT with user info
          const token = jwt.sign(
            { 
              sub: user.id.toString(),
              userId: user.id,
              username: user.username 
            },
            JWT_SECRET,
            { expiresIn: '24h' }
          );

          // Set token in cookie for navigation
          // CRITICAL: Set cookie with proper settings for cross-origin requests
          res.cookie('authToken', token, { 
            httpOnly: false, 
            maxAge: 24 * 60 * 60 * 1000,
            path: '/',
            sameSite: 'lax'  // Allow cookie to be sent with cross-site requests
          });
          
          console.log(`Registration Saga completed successfully for user: ${username}`);
          return res.status(201).json({ 
            token, 
            user,
            saga_id,
            message: 'Registration completed via Saga Orchestrator'
          });
        } else if (status === 'FAILURE') {
          // Saga failed - check if compensation was executed
          const errorMsg = error || result?.error || 'Registration saga failed';
          const compensationExecuted = result?.compensation?.executed || false;
          
          console.error(`Registration Saga failed: ${errorMsg}`);
          console.log(`Compensation executed: ${compensationExecuted}`);
          
          return res.status(400).json({ 
            error: errorMsg,
            saga_id,
            compensation_executed: compensationExecuted,
            message: 'Registration failed - transaction rolled back via Saga compensation'
          });
        }
        // Status is PENDING, continue polling
        attempts++;
      } catch (pollError) {
        console.error(`Error polling saga status: ${pollError.message}`);
        attempts++;
      }
    }

    // Timeout - saga took too long
    // Return 202 with status endpoint so frontend can poll
    return res.status(202).json({ 
      saga_id,
      task_id,
      status: 'pending',
      message: 'Registration is being processed asynchronously. Use /auth/register/status/<task_id> to check status.',
      status_url: `/auth/register/status/${task_id}`
    });

  } catch (error) {
    if (error.response) {
      // Forward error from Saga Orchestrator or other services
      const status = error.response.status;
      const errorData = error.response.data || { error: 'Registration failed' };
      return res.status(status).json(errorData);
    }
    console.error('Register error:', error.message);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Registration status endpoint (Option A - async status checking)
app.get('/auth/register/status/:task_id', async (req, res) => {
  try {
    const { task_id } = req.params;
    
    const statusResponse = await axios.get(`${SAGA_ORCHESTRATOR_URL}/saga/status/${task_id}`);
    const { status, result, error } = statusResponse.data;
    
    if (status === 'SUCCESS') {
      const sagaResult = result?.result || result;
      const user = sagaResult?.user;
      
      if (!user) {
        return res.status(500).json({ 
          error: 'Saga completed but no user data returned',
          status: 'error'
        });
      }
      
      // Sign JWT with user info
      const token = jwt.sign(
        { 
          sub: user.id.toString(),
          userId: user.id,
          username: user.username 
        },
        JWT_SECRET,
        { expiresIn: '24h' }
      );
      
      // Set token in cookie for navigation
      // CRITICAL: Set cookie with proper settings for cross-origin requests
      res.cookie('authToken', token, { 
        httpOnly: false, 
        maxAge: 24 * 60 * 60 * 1000,
        path: '/',
        sameSite: 'lax'  // Allow cookie to be sent with cross-site requests
      });
      
      return res.json({ 
        status: 'completed',
        token, 
        user,
        message: 'Registration completed successfully'
      });
    } else if (status === 'FAILURE') {
      const errorMsg = error || result?.error || 'Registration saga failed';
      return res.status(400).json({ 
        status: 'failed',
        error: errorMsg,
        message: 'Registration failed - transaction rolled back via Saga compensation'
      });
    } else {
      // Still pending
      return res.json({ 
        status: 'pending',
        message: 'Registration is still processing'
      });
    }
  } catch (error) {
    console.error('Error checking registration status:', error.message);
    return res.status(500).json({ 
      error: 'Failed to check registration status',
      status: 'error'
    });
  }
});

// Middleware to extract user_id from JWT and add to headers
const jwtMiddleware = (req, res, next) => {
  let token = null;
  
  // Check Authorization header first
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    token = authHeader.substring(7);
  }
  
  // Check cookie as fallback (for navigation/GET requests)
  if (!token && req.cookies && req.cookies.authToken) {
    token = req.cookies.authToken;
  }
  
  if (token) {
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      const userId = decoded.sub || decoded.userId || '';
      req.headers['x-user-id'] = userId;
      req.headers['X-User-Id'] = userId;
    } catch (error) {
      req.headers['x-user-id'] = '';
      req.headers['X-User-Id'] = '';
    }
  } else {
    req.headers['x-user-id'] = '';
    req.headers['X-User-Id'] = '';
  }
  
  next();
};

// Middleware to apply JWT extraction only to non-auth routes
const applyJwtMiddleware = (req, res, next) => {
  // Skip JWT middleware for auth routes
  if (req.path.startsWith('/auth/')) {
    return next();
  }
  jwtMiddleware(req, res, next);
};

// Proxy to Quiz Service with JWT middleware (excluding /auth routes)
app.use(applyJwtMiddleware);

// Middleware to normalize X-User-Id header before proxy
app.use((req, res, next) => {
  // Ensure X-User-Id header is set with correct case
  if (req.headers['x-user-id'] && !req.headers['X-User-Id']) {
    req.headers['X-User-Id'] = req.headers['x-user-id'];
  }
  
  // Ensure Cookie header is preserved (should be automatic, but just in case)
  // The proxy should forward cookies automatically, but we want to make sure
  if (req.headers.cookie) {
    // Cookies are already in the header, proxy will forward them
  }
  
  next();
});

// Create proxy middleware for all non-auth routes
app.use(createProxyMiddleware({
  target: QUIZ_SERVICE_URL,
  changeOrigin: true,
  preserveHeaderKeyCase: true,
  followRedirects: false, // Let browser handle redirects to preserve cookies
  autoRewrite: true, // Rewrite redirects to go through Gateway
  filter: (pathname, req) => {
    // Only proxy non-auth routes
    return !pathname.startsWith('/auth/');
  },
  // Explicitly forward X-User-Id header to Quiz Service
  onProxyReq: (proxyReq, req, res) => {
    // CRITICAL: Explicitly set X-User-Id header for proxy request
    const userId = req.headers['x-user-id'] || req.headers['X-User-Id'] || '';
    if (userId) {
      proxyReq.setHeader('X-User-Id', userId);
    }
    
    // Ensure cookies are forwarded (should be automatic, but verify)
    if (req.headers.cookie) {
      // Cookies are already being forwarded by the proxy middleware
    }
  },
  onProxyRes: (proxyRes, req, res) => {
    // Forward and fix Set-Cookie headers from Flask for proper session handling
    if (proxyRes.headers['set-cookie']) {
      proxyRes.headers['set-cookie'] = proxyRes.headers['set-cookie'].map(cookie => {
        // Remove domain restrictions and ensure cookie works with Gateway
        let fixed = cookie
          .replace(/;\s*Domain=[^;]+/gi, '')
          .replace(/;\s*Secure/gi, ''); // Remove Secure flag if present (for localhost)
        // Ensure SameSite is set appropriately
        if (!fixed.includes('SameSite')) {
          fixed += '; SameSite=Lax';
        }
        return fixed;
      });
    }
    
    // Handle redirects - rewrite Location header if needed to go through Gateway
    if (proxyRes.headers.location && proxyRes.statusCode >= 300 && proxyRes.statusCode < 400) {
      const location = proxyRes.headers.location;
      // If location is absolute to Flask (port 5000), rewrite to Gateway (port 8080)
      if (location.includes('://localhost:5000') || location.includes('://127.0.0.1:5000')) {
        proxyRes.headers.location = location.replace(/https?:\/\/[^\/]+/, 'http://localhost:8080');
      }
      // Relative URLs should work as-is (autoRewrite handles them)
    }
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err.message);
    if (!res.headersSent) {
      res.status(500).send('Proxy error: Cannot connect to Quiz Service on port 5000. Make sure Flask is running.');
    }
  }
}));

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Gateway server running on port ${PORT}`);
  console.log(`Login endpoint: http://localhost:${PORT}/auth/login`);
  console.log(`Register endpoint: http://localhost:${PORT}/auth/register`);
  console.log(`Quiz Service proxied at: http://localhost:${PORT}/`);
});