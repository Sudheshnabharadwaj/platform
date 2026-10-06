import type { User, Ticket, DashboardStats, AddUserFormData, TicketHistoryItem } from '../types';

// Initial Mock Users Data
export const mockUsers: User[] = [
  {
    id: 'usr-1',
    employeeId: 'ADM001',
    name: 'Hyma',
    email: 'hyma@company.com',
    phone: '+1 (555) 019-2834',
    department: 'IT Support',
    role: 'Admin',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-01-15'
  },
  {
    id: 'usr-2',
    employeeId: 'TL001',
    name: 'Manikanta',
    email: 'manikanta@company.com',
    phone: '+1 (555) 014-9921',
    department: 'IT Support',
    role: 'Team Lead',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-02-01'
  },
  {
    id: 'usr-3',
    employeeId: 'TL005',
    name: 'Adi',
    email: 'adi@company.com',
    phone: '+1 (555) 018-3342',
    department: 'HR',
    role: 'Team Lead',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-03-10'
  },
  {
    id: 'usr-4',
    employeeId: 'EMP004',
    name: 'Sudha',
    email: 'sudha@company.com',
    phone: '+1 (555) 012-7744',
    department: 'Finance',
    role: 'Employee',
    teamLead: 'David Miller (TL003)',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-04-12'
  },
  {
    id: 'usr-5',
    employeeId: 'EMP005',
    name: 'Mounika',
    email: 'mounika@company.com',
    phone: '+1 (555) 016-5589',
    department: 'Operations',
    role: 'Employee',
    teamLead: 'Mounika (Ops Lead)',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-09-20'
  },
  {
    id: 'usr-6',
    employeeId: 'EMP001',
    name: 'Kotesh',
    email: 'kotesh@company.com',
    phone: '+1 (555) 017-8899',
    department: 'IT Support',
    role: 'Employee',
    teamLead: 'Sarah Connor (TL001)',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-08-14'
  },
  {
    id: 'usr-7',
    employeeId: 'TL008',
    name: 'Uday',
    email: 'uday@company.com',
    phone: '+1 (555) 013-4411',
    department: 'Facilities',
    role: 'Team Lead',
    status: 'Active',
    avatarUrl: '',
    createdAt: '2026-07-02'
  }
];

// Initial Mock Tickets Data
export const mockTickets: Ticket[] = [
  {
    id: 't-101',
    ticketNumber: 'TICK-1001',
    title: 'VPN Connection Failure on MacOS Sequoia',
    description: 'User unable to establish secure gateway tunnel after system update.',
    requesterName: 'Sudha',
    requesterEmail: 'sudha@company.com',
    assignedTo: 'Manikanta',
    department: 'IT Support',
    category: 'Network & Connectivity',
    priority: 'High',
    status: 'In Progress',
    slaStatus: 'Normal',
    createdAt: '2026-09-22 09:30',
    dueDate: '2026-09-22 17:30'
  },
  {
    id: 't-102',
    ticketNumber: 'TICK-1002',
    title: 'Payroll Software Access Denied',
    description: 'Finance department user lacks permission for Q3 audit logs.',
    requesterName: 'Mounika',
    requesterEmail: 'mounika@company.com',
    assignedTo: 'Hyma',
    department: 'Finance',
    category: 'Access & Permissions',
    priority: 'Urgent',
    status: 'Escalated',
    slaStatus: 'SLA Risk',
    createdAt: '2026-09-21 14:15',
    dueDate: '2026-09-22 18:00'
  },
  {
    id: 't-103',
    ticketNumber: 'TICK-1003',
    title: 'New Employee Laptop Setup - Onboarding',
    description: 'Hardware provisioning for incoming Sr. Product Designer.',
    requesterName: 'Adi',
    requesterEmail: 'adi@company.com',
    assignedTo: 'Manikanta',
    department: 'HR',
    category: 'Hardware Procurement',
    priority: 'Medium',
    status: 'Open',
    slaStatus: 'Normal',
    createdAt: '2026-09-22 11:00',
    dueDate: '2026-09-24 12:00'
  },
  {
    id: 't-104',
    ticketNumber: 'TICK-1004',
    title: 'Database Timeout Error during Export',
    description: 'Production DB server connection resets during heavy CSV dumps.',
    requesterName: 'Kotesh',
    requesterEmail: 'kotesh@company.com',
    assignedTo: 'Hyma',
    department: 'IT Support',
    category: 'Infrastructure',
    priority: 'Urgent',
    status: 'Escalated',
    slaStatus: 'SLA Breached',
    createdAt: '2026-09-19 16:45',
    dueDate: '2026-09-20 16:45'
  },
  {
    id: 't-105',
    ticketNumber: 'TICK-1005',
    title: 'Building Pass Replacement Request',
    description: 'Physical badge replacement required after lost wallet.',
    requesterName: 'Uday',
    requesterEmail: 'uday@company.com',
    assignedTo: 'Sudha',
    department: 'Facilities',
    category: 'Physical Security',
    priority: 'Low',
    status: 'Resolved',
    slaStatus: 'Normal',
    createdAt: '2026-09-20 08:20',
    dueDate: '2026-09-22 17:00'
  },
  {
    id: 't-106',
    ticketNumber: 'TICK-1006',
    title: 'Warehouse Logistics Dispatch Delay',
    description: 'Inventory sync issue causing order processing delays.',
    requesterName: 'Mounika',
    requesterEmail: 'mounika@company.com',
    assignedTo: 'Mounika',
    department: 'Operations',
    category: 'Supply Chain',
    priority: 'High',
    status: 'In Progress',
    slaStatus: 'Normal',
    createdAt: '2026-09-23 10:15',
    dueDate: '2026-09-25 10:15'
  }
];

export const mockDashboardStats: DashboardStats = {
  totalTickets: 148,
  totalUsers: 64,
  openTickets: 32,
  escalatedTickets: 8,
  slaRiskCount: 5,
  slaBreachedCount: 3,
  resolvedTodayCount: 19
};

const STORAGE_KEY_ADMIN_TICKETS = 'admin_standalone_tickets';

function getStoredTickets(): Ticket[] {
  const cached = localStorage.getItem(STORAGE_KEY_ADMIN_TICKETS);
  if (!cached) {
    localStorage.setItem(STORAGE_KEY_ADMIN_TICKETS, JSON.stringify(mockTickets));
    return mockTickets;
  }
  try {
    return JSON.parse(cached);
  } catch {
    return mockTickets;
  }
}

function saveStoredTickets(tickets: Ticket[]) {
  localStorage.setItem(STORAGE_KEY_ADMIN_TICKETS, JSON.stringify(tickets));
}

// API Service Functions
export const AdminApiService = {
  async getDashboardStats(): Promise<DashboardStats> {
    const tickets = getStoredTickets();
    const openTickets = tickets.filter(t => t.status === 'Open').length;
    const escalatedTickets = tickets.filter(t => t.status === 'Escalated').length;
    const slaRiskCount = tickets.filter(t => t.slaStatus === 'SLA Risk').length;
    const slaBreachedCount = tickets.filter(t => t.slaStatus === 'SLA Breached').length;

    return new Promise((resolve) =>
      setTimeout(
        () =>
          resolve({
            totalTickets: tickets.length,
            totalUsers: 64,
            openTickets,
            escalatedTickets,
            slaRiskCount,
            slaBreachedCount,
            resolvedTodayCount: 19,
          }),
        100
      )
    );
  },

  async getUsers(): Promise<User[]> {
    return new Promise((resolve) => setTimeout(() => resolve(mockUsers), 100));
  },

  async addUser(data: AddUserFormData): Promise<User> {
    return new Promise((resolve, reject) => {
      const cleanEmpId = data.employeeId.trim().toUpperCase();
      const duplicate = mockUsers.some(
        (u) => u.employeeId?.toUpperCase() === cleanEmpId
      );
      if (duplicate) {
        reject(new Error('Employee ID already exists.'));
        return;
      }

      const newUser: User = {
        id: `usr-${Date.now()}`,
        employeeId: cleanEmpId,
        name: data.name,
        email: data.email,
        phone: data.phone,
        department: data.department,
        role: data.role,
        teamLead: data.teamLead,
        status: data.sendEmailInvite ? 'Pending Invitation' : 'Active',
        createdAt: new Date().toISOString().split('T')[0]
      };
      mockUsers.unshift(newUser);
      resolve(newUser);
    });
  },

  async getTickets(filterType?: string): Promise<Ticket[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const tickets = getStoredTickets();
        if (!filterType || filterType === 'all') {
          resolve(tickets);
        } else if (filterType === 'open') {
          resolve(tickets.filter(t => t.status === 'Open'));
        } else if (filterType === 'escalated') {
          resolve(tickets.filter(t => t.status === 'Escalated'));
        } else if (filterType === 'sla-risk') {
          resolve(tickets.filter(t => t.slaStatus === 'SLA Risk'));
        } else if (filterType === 'sla-breached') {
          resolve(tickets.filter(t => t.slaStatus === 'SLA Breached'));
        } else {
          resolve(tickets);
        }
      }, 100);
    });
  },

  async getTicketById(idOrNum: string): Promise<Ticket | null> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const tickets = getStoredTickets();
        const found = tickets.find(
          (t) => t.id === idOrNum || t.ticketNumber.toLowerCase() === idOrNum.toLowerCase()
        );
        resolve(found || null);
      }, 100);
    });
  },

  async createTicket(data: {
    title: string;
    category: string;
    department: any;
    departments?: string[];
    priority: any;
    description: string;
    attachments?: string[];
    assignedTeamLead?: string;
    teamLeads?: { id: string; name: string; role: string; employeeId: string; email: string }[];
    employees?: { id: string; name: string; role: string; employeeId: string; email: string }[];
  }): Promise<Ticket> {
    return new Promise((resolve) => {
      const tickets = getStoredTickets();
      const now = new Date();
      const formatted = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
      const nextNum = 1001 + tickets.length;

      const teamLeadSummary = data.teamLeads && data.teamLeads.length > 0
        ? data.teamLeads.map((tl) => `${tl.name} (${tl.role})`).join(', ')
        : data.assignedTeamLead || 'Sarah Connor (IT Support Team Lead)';

      const employeeSummary = data.employees && data.employees.length > 0
        ? data.employees.map((emp) => `${emp.name} (${emp.employeeId})`).join(', ')
        : 'Unassigned';

      const historyEntries: TicketHistoryItem[] = [
        {
          id: `h-${Date.now()}-1`,
          author: 'Hyma (Admin)',
          text: 'Ticket created.',
          timestamp: formatted,
        },
        {
          id: `h-${Date.now()}-2`,
          author: 'System Routing Engine',
          text: `Routed to Team Lead(s): ${teamLeadSummary}`,
          timestamp: formatted,
        },
      ];

      if (data.employees && data.employees.length > 0) {
        historyEntries.push({
          id: `h-${Date.now()}-3`,
          author: 'System Routing Engine',
          text: `Assigned / Tagged Employee(s): ${employeeSummary}`,
          timestamp: formatted,
        });
      }

      const newTicket: Ticket = {
        id: `t-${Date.now()}`,
        ticketNumber: `TICK-${nextNum}`,
        title: data.title,
        description: data.description,
        requesterName: 'Hyma (Admin)',
        requesterEmail: 'hyma@company.com',
        assignedTo: employeeSummary !== 'Unassigned' ? employeeSummary : 'Hyma',
        assignedTeamLead: teamLeadSummary,
        department: data.department || 'IT Support',
        departments: data.departments,
        category: data.category || 'General Support',
        priority: data.priority || 'Medium',
        status: 'Open',
        slaStatus: 'Normal',
        createdAt: formatted,
        updatedAt: formatted,
        dueDate: formatted,
        attachments: data.attachments || [],
        teamLeads: data.teamLeads,
        employees: data.employees,
        history: historyEntries,
      };

      const updatedList = [newTicket, ...tickets];
      saveStoredTickets(updatedList);
      resolve(newTicket);
    });
  },

  async updateTicket(
    ticketId: string,
    updates: Partial<Ticket>,
    activityNote?: string
  ): Promise<Ticket> {
    return new Promise((resolve, reject) => {
      const tickets = getStoredTickets();
      const index = tickets.findIndex((t) => t.id === ticketId || t.ticketNumber === ticketId);
      if (index === -1) {
        reject(new Error('Ticket not found'));
        return;
      }

      const existing = tickets[index];
      const history = [...(existing.history || [])];

      const now = new Date();
      const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      if (activityNote) {
        history.unshift({
          id: `hist-${Date.now()}-${Math.random()}`,
          author: 'Hyma (Admin)',
          text: activityNote,
          timestamp,
        });
      }

      const updated: Ticket = {
        ...existing,
        ...updates,
        updatedAt: timestamp,
        history,
      };

      tickets[index] = updated;
      saveStoredTickets(tickets);
      resolve(updated);
    });
  },

  async addComment(ticketId: string, text: string, attachmentName?: string): Promise<Ticket | null> {
    return new Promise((resolve) => {
      const tickets = getStoredTickets();
      const index = tickets.findIndex((t) => t.id === ticketId || t.ticketNumber === ticketId);
      if (index === -1) {
        resolve(null);
        return;
      }

      const target = tickets[index];
      const now = new Date();
      const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      if (!target.history) target.history = [];
      target.history.unshift({
        id: `h-${Date.now()}`,
        author: 'Hyma (Admin)',
        text,
        timestamp,
        attachment: attachmentName,
      });

      if (attachmentName) {
        if (!target.attachments) target.attachments = [];
        if (!target.attachments.includes(attachmentName)) {
          target.attachments.push(attachmentName);
        }
      }

      target.updatedAt = timestamp;
      tickets[index] = target;
      saveStoredTickets(tickets);
      resolve(target);
    });
  },

  async addAttachment(ticketId: string, fileName: string): Promise<Ticket | null> {
    return new Promise((resolve) => {
      const tickets = getStoredTickets();
      const index = tickets.findIndex((t) => t.id === ticketId || t.ticketNumber === ticketId);
      if (index === -1) {
        resolve(null);
        return;
      }

      const target = tickets[index];
      const now = new Date();
      const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      if (!target.attachments) target.attachments = [];
      if (!target.attachments.includes(fileName)) {
        target.attachments.push(fileName);
      }

      if (!target.history) target.history = [];
      target.history.unshift({
        id: `h-${Date.now()}`,
        author: 'Hyma (Admin)',
        text: `Uploaded attachment: ${fileName}`,
        timestamp,
        attachment: fileName,
      });

      target.updatedAt = timestamp;
      tickets[index] = target;
      saveStoredTickets(tickets);
      resolve(target);
    });
  },
};

