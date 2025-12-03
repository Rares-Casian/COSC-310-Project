"use client";

import { RoleDashboard, type RoleDashboardProps } from "../RoleDashboard";

type RoleParam = RoleDashboardProps["role"];

const allowedRoles: RoleParam[] = ["guest", "member", "critic", "moderator", "administrator"];

const roleAliases: Record<string, RoleParam> = {
  admin: "administrator",
  admins: "administrator",
  mod: "moderator",
};

type DashboardPageProps = {
  params: { role: string };
};

export default function RoleDashboardPage({ params }: DashboardPageProps) {
  const normalized = roleAliases[params.role] ?? params.role;
  const role = (allowedRoles.includes(normalized as RoleParam)
    ? normalized
    : "member") as RoleParam;

  return <RoleDashboard role={role} />;
}
