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

// CORS middleware - allow requests from Flask app and same origin
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Credentials', 'true');
  
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
      res.cookie('authToken', token, { httpOnly: false, maxAge: 24 * 60 * 60 * 1000 });
      
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

// Custom register endpoint
app.post('/auth/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }

    // Create user via User Service
    const response = await axios.post(`${USER_SERVICE_URL}/users`, {
      username,
      email,
      password
    });

    if (response.status === 201) {
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
      res.cookie('authToken', token, { httpOnly: false, maxAge: 24 * 60 * 60 * 1000 });
      
      return res.status(201).json({ token, user });
    }
  } catch (error) {
    if (error.response) {
      // Forward error from User Service
      const status = error.response.status;
      const errorData = error.response.data || { error: 'Registration failed' };
      return res.status(status).json(errorData);
    }
    console.error('Register error:', error.message);
    return res.status(500).json({ error: 'Internal server error' });
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
      // Add user_id to request headers for Quiz Service
      req.headers['x-user-id'] = decoded.sub || decoded.userId || '';
    } catch (error) {
      // Invalid token - continue without user_id (anonymous access)
      req.headers['x-user-id'] = '';
    }
  } else {
    // No token - anonymous access
    req.headers['x-user-id'] = '';
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
  // Don't modify headers in onProxyReq - let proxy forward them automatically
  onProxyReq: (proxyReq, req, res) => {
    // Ensure cookies are forwarded (should be automatic, but verify)
    if (req.headers.cookie) {
      // Cookies are already being forwarded by the proxy middleware
    }
    
    // Log for debugging
    if (req.method === 'POST') {
      console.log(`Proxying ${req.method} ${req.path} to Quiz Service`);
    }
    if (req.path.includes('/question')) {
      console.log(`Proxying ${req.method} ${req.path} - Cookies: ${req.headers.cookie ? 'present' : 'missing'}`);
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