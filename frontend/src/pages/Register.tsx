import React from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  TextInput,
  PasswordInput,
  Paper,
  Title,
  Container,
  Button,
  Text,
  Stack,
  Alert,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconAlertCircle } from '@tabler/icons-react';
import { useAuth } from '../contexts/AuthContext';

interface RegisterForm {
  email: string;
  password: string;
  fullName: string;
}

export function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [error, setError] = React.useState<string | null>(null);

  const form = useForm<RegisterForm>({
    initialValues: {
      email: '',
      password: '',
      fullName: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      password: (value) => (value.length < 6 ? 'Password must be at least 6 characters' : null),
      fullName: (value) => (value.length < 2 ? 'Name must be at least 2 characters' : null),
    },
  });

  const handleSubmit = async (values: RegisterForm) => {
    try {
      setError(null);
      await register(values.email, values.password, values.fullName);
      navigate('/databases');
    } catch (error: any) {
      console.error('Registration failed:', error);
      setError(error.message);
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">Create an account</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Already have an account?{' '}
        <Text component={RouterLink} to="/login" size="sm" style={{ textDecoration: 'underline' }}>
          Sign in
        </Text>
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        {error && (
          <Alert icon={<IconAlertCircle size={16} />} color="red" mb="md">
            {error}
          </Alert>
        )}
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <TextInput
              required
              label="Full Name"
              placeholder="John Doe"
              {...form.getInputProps('fullName')}
            />
            <TextInput
              required
              label="Email"
              placeholder="your@email.com"
              {...form.getInputProps('email')}
            />
            <PasswordInput
              required
              label="Password"
              placeholder="Your password"
              {...form.getInputProps('password')}
            />
            <Button type="submit" fullWidth mt="xl">
              Create account
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
} 