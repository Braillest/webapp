<?php

namespace App\Controller;

use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Contracts\HttpClient\HttpClientInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class NotificationController extends AbstractController
{
    private HttpClientInterface $client;
    private EntityManagerInterface $entityManager;

    public function __construct(HttpClientInterface $client, EntityManagerInterface $entityManager)
    {
        $this->client = $client;
        $this->entityManager = $entityManager;
    }

    // Forward request to notification backend
    #[Route('/subscribe', name: 'subscribe')]
    public function subscribe(Request $request): Response
    {
        $notification_backend_subscribe_endpoint = 'http://192.168.1.4:3000/subscribe';

        // Extract headers
        $headers = [];
        foreach ($request->headers->all() as $key => $values) {
            $headers[$key] = implode(', ', $values);
        }

        // Forward request to notification backend
        $response = $this->client->request('POST', $notification_backend_subscribe_endpoint, [
            'body' => $request->getContent(),
            'headers' => $headers
        ]);

        // Relay back the response
        return $this->json($response);
    }
}
