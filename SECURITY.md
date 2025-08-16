# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting Security Vulnerabilities

If you discover a security vulnerability within the Evolve Payments Platform, please send an email to your security team. All security vulnerabilities will be promptly addressed.

## Security Measures

### Application Security
- **Authentication**: Django's built-in authentication system with token-based API authentication
- **Authorization**: Role-based access control (Admin, Business, Reseller)
- **Data Protection**: Environment variables for sensitive configuration
- **API Security**: CSRF protection, rate limiting (planned)
- **Input Validation**: Django form validation and serializers

### Dependency Management
- **Regular Updates**: Dependencies are regularly updated to address security vulnerabilities
- **Security Scanning**: Trivy security scanner monitors for known vulnerabilities
- **Minimum Versions**: Security-critical packages specify minimum secure versions

### Current Security Status

#### ✅ Addressed Issues
- **setuptools vulnerabilities**: Updated to version 80.9.0+ (addresses CVE path traversal and RCE issues)
- **Django version**: Using latest stable Django 5.2.5 
- **Dependency updates**: All application dependencies updated to latest secure versions

#### ⚠️ Filtered Issues
- **Kernel vulnerabilities**: System-level issues filtered out as they're infrastructure concerns, not application vulnerabilities
- **OS-level issues**: Handled at the infrastructure/deployment level

### Security Best Practices

1. **Environment Variables**: Never commit sensitive data like API keys or database passwords
2. **Regular Updates**: Keep all dependencies updated with `pip install -r requirements.txt --upgrade`
3. **Access Control**: Use proper Django permissions and user roles
4. **HTTPS**: Always use HTTPS in production
5. **Input Validation**: Validate all user inputs through Django forms/serializers

### Security Scanning

The project uses Trivy for vulnerability scanning. To run security scans:

```bash
# Install trivy (if not already installed)
# Then scan for vulnerabilities
trivy fs . --ignore-unfixed
```

**Note**: The `.trivyignore` file filters out kernel-level vulnerabilities that are not relevant to our Django application and should be handled at the infrastructure level.

### Incident Response

In case of a security incident:
1. Immediately assess the scope and impact
2. Implement temporary mitigation measures
3. Develop and deploy permanent fixes
4. Document the incident and lessons learned
5. Review and update security measures

## Security Updates

This document and security measures are reviewed and updated regularly. Last updated: August 2025.
