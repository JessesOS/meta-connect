import os
import time
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.exceptions import FacebookRequestError


class MetaClient:
    def __init__(self):
        FacebookAdsApi.init(
            app_id=os.environ["META_APP_ID"],
            app_secret=os.environ["META_APP_SECRET"],
            access_token=os.environ["META_ACCESS_TOKEN"],
        )
        self.ad_account_id = os.environ["META_AD_ACCOUNT_ID"]
        self.account = AdAccount(self.ad_account_id)

    def _retry(self, fn, retries=3):
        for attempt in range(retries):
            try:
                return fn()
            except FacebookRequestError as e:
                if e.api_error_code() in (17, 32, 613) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    # ── Campaigns ──────────────────────────────────────────────────────────────

    def get_campaigns(self, status_filter=None):
        params = {"fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time"}
        if status_filter:
            params["effective_status"] = status_filter
        return self._retry(lambda: self.account.get_campaigns(params=params))

    def create_campaign(self, name, objective, daily_budget=None, lifetime_budget=None):
        campaign = Campaign(parent_id=self.ad_account_id)
        campaign.update({
            Campaign.Field.name: name,
            Campaign.Field.objective: objective,
            Campaign.Field.status: Campaign.Status.paused,
            Campaign.Field.special_ad_categories: [],
        })
        if daily_budget:
            campaign[Campaign.Field.daily_budget] = int(daily_budget * 100)
        if lifetime_budget:
            campaign[Campaign.Field.lifetime_budget] = int(lifetime_budget * 100)
        return self._retry(lambda: campaign.remote_create())

    def update_campaign(self, campaign_id, **kwargs):
        campaign = Campaign(campaign_id)
        if "daily_budget" in kwargs:
            kwargs["daily_budget"] = int(kwargs["daily_budget"] * 100)
        campaign.update(kwargs)
        return self._retry(lambda: campaign.remote_update())

    def pause_campaign(self, campaign_id):
        return self.update_campaign(campaign_id, status=Campaign.Status.paused)

    def activate_campaign(self, campaign_id):
        return self.update_campaign(campaign_id, status=Campaign.Status.active)

    # ── Ad Sets ────────────────────────────────────────────────────────────────

    def get_adsets(self, campaign_id=None):
        fields = "id,name,status,daily_budget,bid_amount,targeting,optimization_goal,billing_event"
        if campaign_id:
            campaign = Campaign(campaign_id)
            return self._retry(lambda: campaign.get_ad_sets(params={"fields": fields}))
        return self._retry(lambda: self.account.get_ad_sets(params={"fields": fields}))

    # ── Ads ────────────────────────────────────────────────────────────────────

    def get_ads(self, adset_id=None):
        fields = "id,name,status,creative,adset_id,campaign_id"
        if adset_id:
            adset = AdSet(adset_id)
            return self._retry(lambda: adset.get_ads(params={"fields": fields}))
        return self._retry(lambda: self.account.get_ads(params={"fields": fields}))

    # ── Insights ───────────────────────────────────────────────────────────────

    def get_insights(self, level="campaign", date_preset="last_7d", fields=None):
        default_fields = [
            "campaign_id", "campaign_name", "adset_id", "adset_name",
            "impressions", "clicks", "spend", "cpc", "cpm", "ctr",
            "actions", "cost_per_action_type", "reach", "frequency",
        ]
        params = {
            "level": level,
            "date_preset": date_preset,
            "fields": fields or default_fields,
        }
        return self._retry(lambda: self.account.get_insights(params=params))

    def get_insights_by_date_range(self, start_date, end_date, level="campaign"):
        params = {
            "level": level,
            "time_range": {"since": start_date, "until": end_date},
            "fields": [
                "campaign_name", "impressions", "clicks", "spend",
                "cpc", "cpm", "ctr", "actions", "cost_per_action_type",
            ],
        }
        return self._retry(lambda: self.account.get_insights(params=params))
