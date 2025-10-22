import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Copy, DollarSign, Users, TrendingUp, ExternalLink, RefreshCw } from 'lucide-react';
import { affiliateAPI } from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import { formatCurrency, formatDate } from '../lib/utils';
import useAuthStore from '../store/authStore';

const Affiliate = () => {
  const { toast } = useToast();
  const [payoutAmount, setPayoutAmount] = useState('');
  const { isAuthenticated } = useAuthStore();

  // Fetch affiliate dashboard data
  const { data: dashboardResponse, isLoading, refetch } = useQuery({
    queryKey: ['affiliate-dashboard'],
    queryFn: affiliateAPI.getDashboard,
    enabled: isAuthenticated,
  });

  // Fetch commissions
  const { data: commissionsResponse } = useQuery({
    queryKey: ['affiliate-commissions'],
    queryFn: () => affiliateAPI.getCommissions({ limit: 10 }),
    enabled: isAuthenticated,
  });

  // Fetch referrals
  const { data: referralsResponse } = useQuery({
    queryKey: ['affiliate-referrals'],
    queryFn: affiliateAPI.getReferrals,
    enabled: isAuthenticated,
  });

  const dashboardData = dashboardResponse?.data;
  const commissions = commissionsResponse?.data;
  const referrals = referralsResponse?.data?.referrals || [];

  // Generate new affiliate link
  const generateLinkMutation = useMutation({
    mutationFn: affiliateAPI.generateLink,
    onSuccess: () => {
      toast({
        title: "New link generated",
        description: "Your affiliate link has been refreshed successfully.",
      });
      refetch();
    },
    onError: () => {
      toast({
        title: "Failed to generate link",
        description: "Please try again later.",
        variant: "destructive",
      });
    },
  });

  // Request payout
  const payoutMutation = useMutation({
    mutationFn: affiliateAPI.createPayoutRequest,
    onSuccess: () => {
      toast({
        title: "Payout requested",
        description: "Your payout request has been submitted successfully.",
      });
      setPayoutAmount('');
      refetch();
    },
    onError: (error) => {
      toast({
        title: "Payout request failed",
        description: error.response?.data?.detail || "Please try again later.",
        variant: "destructive",
      });
    },
  });

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Affiliate link copied successfully!",
    });
  };

  const handlePayoutRequest = (e) => {
    e.preventDefault();
    const amount = parseFloat(payoutAmount);
    
    if (amount < 50) {
      toast({
        title: "Minimum payout amount",
        description: "Minimum payout amount is $50.00",
        variant: "destructive",
      });
      return;
    }

    if (amount > (dashboardData?.available_balance || 0)) {
      toast({
        title: "Insufficient balance",
        description: "Payout amount exceeds available balance.",
        variant: "destructive",
      });
      return;
    }

    payoutMutation.mutate({ amount });
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Affiliate Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Earn 30% recurring commission on every referral
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(dashboardData?.total_earnings || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              All-time commission earned
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(dashboardData?.available_balance || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Ready for payout
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Referrals</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData?.total_referrals || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              People referred
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(dashboardData?.monthly_earnings || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Commission this month
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Affiliate Link */}
        <Card>
          <CardHeader>
            <CardTitle>Your Affiliate Link</CardTitle>
            <CardDescription>
              Share this link to earn 30% commission on every subscription
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Your Affiliate Link:
              </label>
              <div className="flex gap-2">
                <Input
                  value={dashboardData?.affiliate_link || 'Loading...'}
                  readOnly
                  className="font-mono text-sm bg-gray-50"
                  placeholder="Your affiliate link will appear here"
                />
                <Button
                  onClick={() => copyToClipboard(dashboardData?.affiliate_link || '')}
                  variant="outline"
                  size="icon"
                  disabled={!dashboardData?.affiliate_link}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              {dashboardData?.referral_code && (
                <p className="text-xs text-gray-600">
                  Referral Code: <span className="font-mono font-semibold">{dashboardData.referral_code}</span>
                </p>
              )}
            </div>
            
            <div className="flex gap-2">
              <Button
                onClick={() => generateLinkMutation.mutate()}
                disabled={generateLinkMutation.isPending}
                variant="outline"
                className="flex-1"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${generateLinkMutation.isPending ? 'animate-spin' : ''}`} />
                Generate New Link
              </Button>
              
              <Button
                onClick={() => window.open(dashboardData?.affiliate_link, '_blank')}
                variant="outline"
                disabled={!dashboardData?.affiliate_link}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Preview Link
              </Button>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Share your unique affiliate link with friends and colleagues</li>
                <li>• When someone signs up using your link and subscribes, you earn 30%</li>
                <li>• Commissions are recurring for the lifetime of the subscription</li>
                <li>• Minimum payout is $50 - payments processed monthly</li>
                <li>• Track your earnings and referrals in real-time</li>
              </ul>
            </div>
            
            {!dashboardData?.affiliate_link && (
              <div className="bg-yellow-50 p-4 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Getting started:</strong> Click "Generate New Link" to create your unique affiliate link.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payout Request */}
        <Card>
          <CardHeader>
            <CardTitle>Request Payout</CardTitle>
            <CardDescription>
              Minimum payout amount is $50.00
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePayoutRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payout Amount
                </label>
                <Input
                  type="number"
                  step="0.01"
                  min="50"
                  max={dashboardData?.available_balance || 0}
                  value={payoutAmount}
                  onChange={(e) => setPayoutAmount(e.target.value)}
                  placeholder="Enter amount"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Available: {formatCurrency(dashboardData?.available_balance || 0)}
                </p>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={!payoutAmount || payoutMutation.isPending}
              >
                {payoutMutation.isPending ? 'Processing...' : 'Request Payout'}
              </Button>
            </form>

            <div className="mt-6">
              <h4 className="font-medium mb-2">Recent Payout Requests</h4>
              {dashboardData?.recent_payouts?.length > 0 ? (
                <div className="space-y-2">
                  {dashboardData.recent_payouts.slice(0, 3).map((payout) => (
                    <div key={payout.id} className="flex justify-between items-center text-sm">
                      <span>{formatDate(payout.created_at)}</span>
                      <div className="text-right">
                        <div className="font-medium">{formatCurrency(payout.amount)}</div>
                        <div className={`text-xs ${
                          payout.status === 'completed' ? 'text-green-600' :
                          payout.status === 'pending' ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {payout.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No payout requests yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid lg:grid-cols-2 gap-8 mt-8">
        {/* Recent Commissions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Commissions</CardTitle>
            <CardDescription>
              Your latest commission earnings
            </CardDescription>
          </CardHeader>
          <CardContent>
            {commissions?.commissions?.length > 0 ? (
              <div className="space-y-4">
                {commissions.commissions.map((commission) => (
                  <div key={commission.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">
                        {formatCurrency(commission.amount)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {formatDate(commission.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className={`text-xs px-2 py-1 rounded ${
                        commission.status === 'paid' ? 'bg-green-100 text-green-800' :
                        commission.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {commission.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No commissions yet. Start referring to earn!
              </p>
            )}
          </CardContent>
        </Card>

        {/* Recent Referrals */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Referrals</CardTitle>
            <CardDescription>
              People who signed up through your link
            </CardDescription>
          </CardHeader>
          <CardContent>
            {referrals?.length > 0 ? (
              <div className="space-y-4">
                {referrals.slice(0, 5).map((referral) => (
                  <div key={referral.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">
                        {referral.referred_user_name || 'Anonymous User'}
                      </p>
                      <p className="text-sm text-gray-600">
                        {formatDate(referral.created_at)}
                      </p>
                    </div>
                    <div className={`text-xs px-2 py-1 rounded ${
                      referral.has_subscribed ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {referral.has_subscribed ? 'Subscribed' : 'Signed up'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No referrals yet. Share your link to get started!
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Affiliate;
