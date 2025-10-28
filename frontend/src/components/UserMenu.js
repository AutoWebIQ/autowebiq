import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { User, Settings, Github, HelpCircle, LogOut, MessageSquare } from 'lucide-react';

const UserMenu = ({ user, onLogout }) => {
  const navigate = useNavigate();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="user-menu-trigger" data-testid="user-menu-btn">
          <User size={18} className="mr-2" />
          {user.username}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col">
            <span className="font-semibold">{user.username}</span>
            <span className="text-xs text-gray-500">{user.email}</span>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => navigate('/settings')} data-testid="account-settings-menu">
          <Settings size={16} className="mr-2" />
          Account Settings
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate('/github')} data-testid="github-menu">
          <Github size={16} className="mr-2" />
          Connect to GitHub
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => window.open('https://discord.gg/autowebiq', '_blank')} data-testid="discord-menu">
          <MessageSquare size={16} className="mr-2" />
          Join Discord
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate('/help')} data-testid="help-menu">
          <HelpCircle size={16} className="mr-2" />
          Help Center
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onLogout} data-testid="logout-menu" className="text-red-600">
          <LogOut size={16} className="mr-2" />
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserMenu;
