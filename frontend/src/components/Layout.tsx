import React from 'react';
import { AppShell, Burger, Group, Text, useMantineColorScheme } from '@mantine/core';
import { useAuth } from '../contexts/AuthContext';
import { IconDatabase, IconLogout, IconMoonStars, IconSun } from '@tabler/icons-react';
import { Link, useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [opened, setOpened] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened }
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger
            opened={opened}
            onClick={() => setOpened(!opened)}
            hiddenFrom="sm"
            size="sm"
          />
          <Text size="xl" fw={700}>T2SQL</Text>
          <Group ml="auto">
            <Text
              size="lg"
              fw={500}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
              onClick={() => toggleColorScheme()}
            >
              {colorScheme === 'dark' ? <IconSun size={20} /> : <IconMoonStars size={20} />}
              {colorScheme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </Text>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <AppShell.Section>
          <Link to="/databases" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Text size="lg" fw={500} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <IconDatabase size={20} />
              Databases
            </Text>
          </Link>
        </AppShell.Section>
        <AppShell.Section mt="auto">
          <Text
            size="lg"
            fw={500}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
            onClick={handleLogout}
          >
            <IconLogout size={20} />
            Logout
          </Text>
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main>
        {children}
      </AppShell.Main>
    </AppShell>
  );
} 