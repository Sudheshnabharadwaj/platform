import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AdminLayout } from '../layouts/AdminLayout';
import { DashboardPage } from '../pages/DashboardPage';
import { AddUserPage } from '../pages/AddUserPage';
import { LoginPage } from '../pages/auth/LoginPage';
import { KindOfWorkPage } from '../pages/auth/KindOfWorkPage';
import { SignupPage } from '../pages/auth/SignupPage';
import { ForgotPasswordPage } from '../pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '../pages/auth/ResetPasswordPage';
import { AllTicketsPage } from '../pages/workspace/AllTicketsPage';
import { TicketManagementPage } from '../pages/workspace/TicketManagementPage';
import { EscalatedTicketsPage } from '../pages/workspace/EscalatedTicketsPage';
import { SLARiskPage } from '../pages/workspace/SLARiskPage';
import { SLABreachedPage } from '../pages/workspace/SLABreachedPage';
import { AdminTicketDetailsPage } from '../pages/workspace/AdminTicketDetailsPage';
import { UserManagementPage } from '../pages/administration/UserManagementPage';
import { RolesPermissionsPage } from '../pages/administration/RolesPermissionsPage';
import { TicketConfigPage } from '../pages/administration/TicketConfigPage';
import { WorkflowSettingsPage } from '../pages/administration/WorkflowSettingsPage';
import { SecuritySettingsPage } from '../pages/administration/SecuritySettingsPage';
import { AdminSettingsPage } from '../pages/administration/AdminSettingsPage';
import { ProfilePage } from '../pages/ProfilePage';

import { MyTicketsPage } from '../pages/workspace/MyTicketsPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Root redirect */}
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />

      {/* Admin Authentication & Setup Routes */}
      <Route path="/admin/auth/login" element={<LoginPage />} />
      <Route path="/kind-of-work" element={<KindOfWorkPage />} />
      <Route path="/admin/auth/signup" element={<SignupPage />} />
      <Route path="/admin/auth/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/admin/auth/reset-password" element={<ResetPasswordPage />} />

      {/* Admin Protected Layout Routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="add-user" element={<AddUserPage />} />
        <Route path="settings" element={<AdminSettingsPage />} />

        {/* Workspace Sub-routes */}
        <Route path="workspace/all" element={<AllTicketsPage />} />
        <Route path="workspace/my-tickets" element={<MyTicketsPage />} />
        <Route path="workspace/tickets/:id" element={<AdminTicketDetailsPage />} />
        <Route path="workspace/management" element={<TicketManagementPage />} />
        <Route path="workspace/escalated" element={<EscalatedTicketsPage />} />
        <Route path="workspace/sla-risk" element={<SLARiskPage />} />
        <Route path="workspace/sla-breached" element={<SLABreachedPage />} />

        {/* Administration Sub-routes */}
        <Route path="administration/users" element={<UserManagementPage />} />
        <Route path="administration/roles" element={<RolesPermissionsPage />} />
        <Route path="administration/ticket-config" element={<TicketConfigPage />} />
        <Route path="administration/workflows" element={<WorkflowSettingsPage />} />
        <Route path="administration/security" element={<SecuritySettingsPage />} />
      </Route>

      {/* Fallback Catch-all Route */}
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  );
};

