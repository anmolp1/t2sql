import React, { useState } from 'react';
import {
  Container,
  Title,
  Paper,
  Textarea,
  Button,
  Stack,
  Text,
  Select,
  Code,
  Group,
  ActionIcon,
  useMantineTheme,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconCopy, IconRefresh } from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { getDatabaseConnections } from '../services/api';
import { generateSQLQuery } from '../services/api';

interface DatabaseConnection {
  id: number;
  name: string;
  connection_type: string;
  host: string;
  port: string;
  database_name: string;
  username: string;
}

interface QueryForm {
  question: string;
  database_id: string;
}

interface QueryResponse {
  query: string;
}

export function QueryGenerator() {
  const theme = useMantineTheme();
  const [generatedQuery, setGeneratedQuery] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const form = useForm<QueryForm>({
    initialValues: {
      question: '',
      database_id: '',
    },
    validate: {
      question: (value) => (!value ? 'Question is required' : null),
      database_id: (value) => (!value ? 'Database is required' : null),
    },
  });

  const { data: connections = [] } = useQuery<DatabaseConnection[]>({
    queryKey: ['databaseConnections'],
    queryFn: async () => {
      const response = await getDatabaseConnections();
      return response.data;
    },
  });

  const databaseOptions = connections.map((connection: DatabaseConnection) => ({
    value: connection.id.toString(),
    label: connection.name,
  }));

  const handleSubmit = async (values: QueryForm) => {
    setIsGenerating(true);
    try {
      const databaseId = Number(values.database_id);
      if (isNaN(databaseId)) {
        throw new Error('Invalid database ID');
      }
      const response = await generateSQLQuery(databaseId, values.question);
      setGeneratedQuery(response.data.query);
    } catch (error) {
      console.error('Error generating SQL query:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedQuery) {
      navigator.clipboard.writeText(generatedQuery);
    }
  };

  return (
    <Container size="lg">
      <Title mb="xl">SQL Query Generator</Title>

      <Paper p="md" radius="md" withBorder>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <Select
              required
              label="Select Database"
              placeholder="Choose a database"
              data={databaseOptions}
              {...form.getInputProps('database_id')}
            />
            <Textarea
              required
              label="Your Question"
              placeholder="Ask a question about your data..."
              minRows={4}
              {...form.getInputProps('question')}
            />
            <Button
              type="submit"
              loading={isGenerating}
              leftSection={<IconRefresh size={14} />}
            >
              Generate SQL Query
            </Button>
          </Stack>
        </form>
      </Paper>

      {generatedQuery && (
        <Paper p="md" radius="md" withBorder mt="xl">
          <Group justify="space-between" mb="md">
            <Text fw={500}>Generated SQL Query</Text>
            <ActionIcon
              variant="light"
              color="blue"
              onClick={copyToClipboard}
            >
              <IconCopy size={16} />
            </ActionIcon>
          </Group>
          <Code block>{generatedQuery}</Code>
        </Paper>
      )}
    </Container>
  );
} 