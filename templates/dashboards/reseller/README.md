# Reseller Dashboard Template Documentation

## Overview
This document outlines the updates made to the reseller dashboard template files to address layout issues and improve consistency in styling.

## Changes Made

### 1. Sidebar
- **Adjustment:** The sidebar's height was adjusted to `calc(100vh - header height)` with a `top` offset equivalent to the header's height.
- **Consolidation:** Multiple sidebar CSS definitions were consolidated into a single `.sidebar` class with CSS variables to manage width and colors.

### 2. Header
- **Position:** The header is fixed at the top, spans the full width, has adequate height and padding.
- **Style Enhancements:** Improved alignment and spacing for components such as the welcome message, search bar, notifications, user dropdown, and help link.

### 3. Main Content
- **Margin Adjustment:** Adjustments were made to account for both sidebar width and header height using CSS variables to avoid overlapping.

## Purpose
These changes were made to resolve overlapping elements and misalignments in the layout, providing a more consistent and visually appealing user interface.

## Current System
With these changes, the layout is expected to be:
- Responsive to different screen sizes
- Consistent across various components
- Maintainable with the use of CSS variables

## Recommended Future Actions
- Eliminate any conflicting styles in other CSS files or components.
- Continue using CSS variables for consistent widths and spacing.
- Ensure all interactive components respect layout offsets.
