import React, { useState, useEffect } from 'react';
import {
  Container,
  Title,
  Button,
  Group,
  Paper,
  Text,
  Modal,
  TextInput,
  Select,
  Stack,
  ActionIcon,
  useMantineTheme,
  Textarea,
  Alert,
  Loader,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconPlus, IconTrash, IconEdit, IconDatabase, IconAlertCircle } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AxiosError, AxiosResponse } from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  getDatabaseConnections,
  createDatabaseConnection,
  deleteDatabaseConnection,
  extractDatabaseMetadata,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface DatabaseConnection {
  id: number;
  name: string;
  connection_type: string;
  host?: string;
  port?: string;
  database_name?: string;
  username?: string;
  project_id?: string;
  dataset?: string;
  credentials_json?: string;
}

interface ConnectionForm {
  name: string;
  connection_type: string;
  host?: string;
  port?: string;
  database_name?: string;
  username?: string;
  project_id?: string;
  dataset?: string;
  credentials_json?: string;
}

export function DatabaseConnections() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState<DatabaseConnection | null>(null);
  const theme = useMantineTheme();
  const navigate = useNavigate();
  const { isAuthenticated, token } = useAuth();
  const queryClient = useQueryClient();

  // Add debug logging
  console.log('Auth state:', { isAuthenticated, token });

  // Move navigation logic to useEffect
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const form = useForm<ConnectionForm>({
    initialValues: {
      name: '',
      connection_type: 'bigquery',
      host: '',
      port: '',
      database_name: '',
      username: '',
      project_id: '',
      dataset: '',
      credentials_json: '',
    },
    validate: {
      name: (value) => (!value ? 'Name is required' : null),
      connection_type: (value) => (!value ? 'Connection type is required' : null),
      project_id: (value, values) => 
        values.connection_type === 'bigquery' && !value ? 'Project ID is required for BigQuery' : null,
      dataset: (value, values) => 
        values.connection_type === 'bigquery' && !value ? 'Dataset is required for BigQuery' : null,
      credentials_json: (value, values) => 
        values.connection_type === 'bigquery' && !value ? 'Credentials JSON is required for BigQuery' : null,
    },
  });

  const { data: connections = [], isLoading, error } = useQuery<DatabaseConnection[]>({
    queryKey: ['databaseConnections'],
    queryFn: async () => {
      console.log('Fetching database connections...');
      const response = await getDatabaseConnections();
      console.log('Database connections response:', response);
      return response.data;
    },
    retry: 1,
    staleTime: 30000, // 30 seconds
  });

  const createMutation = useMutation<AxiosResponse<DatabaseConnection>, AxiosError, ConnectionForm>({
    mutationFn: createDatabaseConnection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databaseConnections'] });
      setIsCreateModalOpen(false);
      form.reset();
    },
    onError: (error: AxiosError) => {
      console.error('Error creating database connection:', error.response?.data);
      if (error.response?.status === 422) {
        const validationErrors = error.response.data as { detail: Array<{ loc: string[], msg: string }> | string };
        if (Array.isArray(validationErrors.detail)) {
          const errorMessages = validationErrors.detail.map((err) => 
            `${err.loc.join('.')}: ${err.msg}`
          ).join('\n');
          alert('Validation errors:\n' + errorMessages);
        } else {
          alert('Validation error: ' + validationErrors.detail);
        }
      } else {
        const errorData = error.response?.data as { detail?: string };
        alert('Error creating database connection: ' + (errorData?.detail || error.message));
      }
    },
  });

  const deleteMutation = useMutation<AxiosResponse<void>, AxiosError, number>({
    mutationFn: deleteDatabaseConnection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databaseConnections'] });
    },
    onError: (error: AxiosError) => {
      console.error('Error deleting database connection:', error.response?.data);
    },
  });

  const extractMetadataMutation = useMutation<AxiosResponse<void>, AxiosError, number>({
    mutationFn: extractDatabaseMetadata,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databaseConnections'] });
    },
    onError: (error: AxiosError) => {
      console.error('Error extracting metadata:', error.response?.data);
    },
  });

  const handleCreate = (values: ConnectionForm) => {
    // Parse credentials_json if it's a string
    const formData = {
      ...values,
      credentials_json: values.credentials_json ? JSON.parse(values.credentials_json) : null
    };
    createMutation.mutate(formData);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this connection?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleExtractMetadata = (id: number) => {
    extractMetadataMutation.mutate(id);
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <Container size="lg" py="xl">
        <Group justify="center">
          <Loader size="xl" />
        </Group>
      </Container>
    );
  }

  if (error) {
    return (
      <Container size="lg" py="xl">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error"
          color="red"
          variant="filled"
        >
          Failed to load database connections. Please try again later.
          {error instanceof AxiosError && error.response?.data?.detail && (
            <Text size="sm" mt="xs">
              {error.response.data.detail}
            </Text>
          )}
        </Alert>
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Group justify="space-between" mb="xl">
        <Title order={1}>Database Connections</Title>
        <Button
          leftSection={<IconPlus size={16} />}
          onClick={() => setIsCreateModalOpen(true)}
        >
          Create Connection
        </Button>
      </Group>

      {connections.length === 0 ? (
        <Paper p="xl" radius="md" withBorder>
          <Group justify="center" gap="xs">
            <IconDatabase size={24} color={theme.colors.gray[5]} />
            <Text color="dimmed">No database connections found</Text>
          </Group>
        </Paper>
      ) : (
        <Stack gap="md">
          {connections.map((connection: DatabaseConnection) => (
            <Paper key={connection.id} p="md" radius="md" withBorder>
              <Group justify="space-between" mb="xs">
                <div>
                  <Text fw={500}>{connection.name}</Text>
                  <Text size="sm" color="dimmed">
                    Type: {connection.connection_type}
                  </Text>
                </div>
                <Group gap="xs">
                  <ActionIcon
                    color="blue"
                    variant="light"
                    onClick={() => handleExtractMetadata(connection.id)}
                    title="Extract Metadata"
                  >
                    <IconDatabase size={16} />
                  </ActionIcon>
                  <ActionIcon
                    color="yellow"
                    variant="light"
                    onClick={() => {
                      setSelectedConnection(connection);
                      setIsEditModalOpen(true);
                    }}
                    title="Edit"
                  >
                    <IconEdit size={16} />
                  </ActionIcon>
                  <ActionIcon
                    color="red"
                    variant="light"
                    onClick={() => handleDelete(connection.id)}
                    title="Delete"
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              </Group>
            </Paper>
          ))}
        </Stack>
      )}

      {/* Create Connection Modal */}
      <Modal
        opened={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Database Connection"
        size="lg"
      >
        <form onSubmit={form.onSubmit(handleCreate)}>
          <Stack gap="md">
            <TextInput
              required
              label="Name"
              placeholder="My Database Connection"
              {...form.getInputProps('name')}
            />
            <Select
              required
              label="Connection Type"
              placeholder="Select connection type"
              data={[
                { value: 'bigquery', label: 'BigQuery' },
                { value: 'postgresql', label: 'PostgreSQL' },
                { value: 'mysql', label: 'MySQL' },
              ]}
              {...form.getInputProps('connection_type')}
            />
            {form.values.connection_type === 'bigquery' && (
              <>
                <TextInput
                  required
                  label="Project ID"
                  placeholder="my-project-id"
                  {...form.getInputProps('project_id')}
                />
                <TextInput
                  required
                  label="Dataset"
                  placeholder="my-dataset"
                  {...form.getInputProps('dataset')}
                />
                <Textarea
                  required
                  label="Credentials JSON"
                  placeholder="Paste your service account credentials JSON here"
                  minRows={4}
                  {...form.getInputProps('credentials_json')}
                />
              </>
            )}
            {form.values.connection_type !== 'bigquery' && (
              <>
                <TextInput
                  label="Host"
                  placeholder="localhost"
                  {...form.getInputProps('host')}
                />
                <TextInput
                  label="Port"
                  placeholder="5432"
                  {...form.getInputProps('port')}
                />
                <TextInput
                  label="Database Name"
                  placeholder="mydb"
                  {...form.getInputProps('database_name')}
                />
                <TextInput
                  label="Username"
                  placeholder="user"
                  {...form.getInputProps('username')}
                />
              </>
            )}
            <Group justify="flex-end" mt="md">
              <Button variant="default" onClick={() => setIsCreateModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={createMutation.isPending}>
                Create
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      {/* Edit Connection Modal */}
      <Modal
        opened={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Database Connection"
        size="lg"
      >
        {selectedConnection && (
          <form onSubmit={form.onSubmit(handleCreate)}>
            <Stack gap="md">
              <TextInput
                required
                label="Name"
                placeholder="My Database Connection"
                defaultValue={selectedConnection.name}
                {...form.getInputProps('name')}
              />
              <Select
                required
                label="Connection Type"
                placeholder="Select connection type"
                data={[
                  { value: 'bigquery', label: 'BigQuery' },
                  { value: 'postgresql', label: 'PostgreSQL' },
                  { value: 'mysql', label: 'MySQL' },
                ]}
                defaultValue={selectedConnection.connection_type}
                {...form.getInputProps('connection_type')}
              />
              {form.values.connection_type === 'bigquery' && (
                <>
                  <TextInput
                    required
                    label="Project ID"
                    placeholder="my-project-id"
                    defaultValue={selectedConnection.project_id}
                    {...form.getInputProps('project_id')}
                  />
                  <TextInput
                    required
                    label="Dataset"
                    placeholder="my-dataset"
                    defaultValue={selectedConnection.dataset}
                    {...form.getInputProps('dataset')}
                  />
                  <Textarea
                    required
                    label="Credentials JSON"
                    placeholder="Paste your service account credentials JSON here"
                    minRows={4}
                    defaultValue={selectedConnection.credentials_json}
                    {...form.getInputProps('credentials_json')}
                  />
                </>
              )}
              {form.values.connection_type !== 'bigquery' && (
                <>
                  <TextInput
                    label="Host"
                    placeholder="localhost"
                    defaultValue={selectedConnection.host}
                    {...form.getInputProps('host')}
                  />
                  <TextInput
                    label="Port"
                    placeholder="5432"
                    defaultValue={selectedConnection.port}
                    {...form.getInputProps('port')}
                  />
                  <TextInput
                    label="Database Name"
                    placeholder="mydb"
                    defaultValue={selectedConnection.database_name}
                    {...form.getInputProps('database_name')}
                  />
                  <TextInput
                    label="Username"
                    placeholder="user"
                    defaultValue={selectedConnection.username}
                    {...form.getInputProps('username')}
                  />
                </>
              )}
              <Group justify="flex-end" mt="md">
                <Button variant="default" onClick={() => setIsEditModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" loading={createMutation.isPending}>
                  Save Changes
                </Button>
              </Group>
            </Stack>
          </form>
        )}
      </Modal>
    </Container>
  );
} 