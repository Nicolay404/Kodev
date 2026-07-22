import { NavLink } from "react-router-dom";
import { cn } from "../../utils/cn";
import { LayoutDashboard, PhoneCall, Activity, Siren, Bell, Settings, ShieldCheck, Bot, FileText, FolderCheck } from "lucide-react";
import { useAuthStore, type Role } from "../../store/authStore";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const CLINICAL_ROLES: Role[] = ['professional', 'nurse', 'center_admin', 'system_admin'];
const TELECONSULT_ROLES: Role[] = ['professional', 'center_admin', 'system_admin'];
const PATIENT_AND_CLINICAL_ROLES: Role[] = ['patient', 'professional', 'nurse', 'center_admin', 'system_admin'];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const role = useAuthStore((state) => state.user?.role);

  const menuItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard, show: true },
    { name: "Asistente de Orientación", path: "/help", icon: Bot, show: role === 'patient' },
    { name: "Emergencias", path: "/emergencies", icon: Siren, show: role && PATIENT_AND_CLINICAL_ROLES.includes(role) },
    { name: "Historial Clínico", path: "/historial", icon: FileText, show: role && PATIENT_AND_CLINICAL_ROLES.includes(role) },
    { name: "Cierre de Casos", path: "/cierre-casos", icon: FolderCheck, show: role && PATIENT_AND_CLINICAL_ROLES.includes(role) },
    { name: "Alertas de Monitoreo", path: "/monitoring", icon: Activity, show: role && CLINICAL_ROLES.includes(role) },
    { name: "Teleconsulta", path: "/teleconsult", icon: PhoneCall, show: role && TELECONSULT_ROLES.includes(role) },
    { name: "Notificaciones", path: "/notifications", icon: Bell, show: true },
    { name: "Administración", path: "/admin", icon: Settings, show: role === 'system_admin' },
    { name: "Auditoría", path: "/audit", icon: ShieldCheck, show: role === 'dpd_delegate' },
  ].filter((item) => item.show);

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-screen w-64 bg-surface border-r border-gray-200 transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <span className="text-lg font-bold text-teal-600">SAMR Central</span>
        </div>
        <nav className="p-4 space-y-1">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              onClick={() => { if (window.innerWidth < 768) onClose(); }}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-teal-50 text-teal-700"
                    : "text-gray-700 hover:bg-gray-100"
                )
              }
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
