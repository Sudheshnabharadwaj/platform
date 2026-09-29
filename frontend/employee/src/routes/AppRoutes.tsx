import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { EmployeeLayout } from '../components/layout/EmployeeLayout';
import { EmployeeSignIn } from '../pages/EmployeeSignIn';
import { EmployeeDashboard } from '../pages/EmployeeDashboard';
import { MyTickets } from '../pages/MyTickets';
import { AssignedTickets } from '../pages/AssignedTickets';
import { AssignedTicketDetails } from '../pages/AssignedTicketDetails';
import { CreateTicket } from '../pages/CreateTicket';
import { KnowledgeBase } from '../pages/KnowledgeBase';
import { Notifications } from '../pages/Notifications';
import { Profile } from '../pages/Profile';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* 1. Employee Sign In */}
      <Route path="/signin" element={<EmployeeSignIn />} />

      {/* 2. Employee Main Portal Layout with Sub-routes */}
      <Route element={<EmployeeLayout />}>
        <Route path="/dashboard" element={<EmployeeDashboard />} />
        <Route path="/knowledge-base" element={<KnowledgeBase />} />
        <Route path="/tickets" element={<MyTickets />} />
        <Route path="/tickets/:id" element={<AssignedTicketDetails />} />
        <Route path="/assigned-tickets" element={<AssignedTickets />} />
        <Route path="/assigned-tickets/:id" element={<AssignedTicketDetails />} />
        <Route path="/create-ticket" element={<CreateTicket />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* Default Route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
