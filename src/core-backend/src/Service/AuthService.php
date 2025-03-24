<?php

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\HttpFoundation\Session\SessionInterface;

class AuthService
{
    public function __construct(EntityManagerInterface $entityManager)
    {
        $this->entityManager = $entityManager;
    }

    public function authorize(SessionInterface $session): bool
    {
        // Missing user_id key case
        if (!$session->get('user_id'))
        {
            return false;
        }

        // Missing expires key case
        if (!$session->get('expires'))
        {
            return false;
        }

        // Expired login key case
        if ($session->get('expires') < new DateTime())
        {
            $this->logout($session);
            return false;
        }

        return true;
    }

    public function authorizeRole(SessionInterface $session, int $role_id): bool
    {
        // Check typical authorization cases first
        $authorized = $this->authorize($session);

        // Missing role_id key case
        if (!$session->get('role_id'))
        {
            return false;
        }

        // Get user
        $user_id = $session->get('user_id');
        $user = $this->entityManager->getRepository(User::class)->findById($user_id);

        // Missing role case
        $roles = $user->getRoles();
        $found = false;
        foreach ($roles as $role)
        {
            if ($role_id == $role->getId())
            {
                $found = true;
                break;
            }
        }

        return $found;
    }

    public function login(SessionInterface $session, string $username, string $password): bool
    {
        $user = $this->entityManager->getRepository(User::class)->findOneBy(['username' => $username]);

        // Invalid username case
        if (!$user)
        {
            return false;
        }

        // Invalid password case
        if (!password_verify($password, $user->getPasswordHash()))
        {
            return false;
        }

        // Set expires key
        // - Valid for one week
        $expiration_date = new DateTime();
        $expiration_date->modify('+1 week');
        $session->set('expires', $expiration_date);

        // Set user_id
        $session->set('user_id', $user->getId());

        // Set role
        $session->set('role_id', $user->getRole()->getId());

        return true;
    }

    public function doesUsernameAlreadyExist(string $username): bool
    {
        $user = $this->entityManager->getRepository(User::class)->findOneBy(['username' => $username]);
        return ($user != null);
    }

    public function register(string $username, string $password): void
    {
        // Username already exists case
        if($this->doesUsernameAlreadyExist($username))
        {
            return;
        }

        $password_hash = password_hash($password, PASSWORD_BCRYPT);

        $user = new User();
        $user->setUsername($username);
        $user->setPassword($password_hash);
        $user->setDateCreated(new DateTime());
        $user->setDateModified(new DateTime());

        $entityManager->persist($user);
        $entityManager->flush();
    }

    // Clears session and performs any other additional logic to logout session
    public function logout(SessionInterface $session): void
    {
        // TODO: Also clear out the session if/when multi logins/sessions are considered/captured

        $session->clear();
    }
}
