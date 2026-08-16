/* ------------------------------------------------------------
name: "trumpet_lead"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn TrumpetLead -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __TrumpetLead_H__
#define  __TrumpetLead_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS TrumpetLead
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class TrumpetLeadSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec8[2];
	
  public:
	
	int getNumInputsTrumpetLeadSIG0() {
		return 0;
	}
	int getNumOutputsTrumpetLeadSIG0() {
		return 1;
	}
	
	void instanceInitTrumpetLeadSIG0(int sample_rate) {
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iVec2[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec8[l7] = 0;
		}
	}
	
	void fillTrumpetLeadSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec8[0] = (iVec2[1] + iRec8[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec8[0]));
			iVec2[1] = iVec2[0];
			iRec8[1] = iRec8[0];
		}
	}

};

static TrumpetLeadSIG0* newTrumpetLeadSIG0() { return (TrumpetLeadSIG0*)new TrumpetLeadSIG0(); }
static void deleteTrumpetLeadSIG0(TrumpetLeadSIG0* dsp) { delete dsp; }

static float TrumpetLead_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0TrumpetLeadSIG0[65536];

class TrumpetLead : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst6;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	float fRec1[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec2[2];
	float fConst11;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst12;
	float fConst14;
	float fConst16;
	float fConst18;
	FAUSTFLOAT fHslider2;
	float fConst19;
	int iRec5[2];
	float fRec4[3];
	float fConst20;
	float fConst21;
	float fConst22;
	float fConst23;
	float fRec9[2];
	FAUSTFLOAT fHslider3;
	float fConst24;
	FAUSTFLOAT fHslider4;
	float fConst25;
	float fRec6[2];
	float fRec3[3];
	float fRec0[3];
	float fConst27;
	float fConst28;
	
 public:
	TrumpetLead() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn TrumpetLead -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "trumpet_lead.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/peak_eq:author", "Julius O. Smith III");
		m->declare("filters.lib/peak_eq:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/peak_eq:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "trumpet_lead");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		TrumpetLeadSIG0* sig0 = newTrumpetLeadSIG0();
		sig0->instanceInitTrumpetLeadSIG0(sample_rate);
		sig0->fillTrumpetLeadSIG0(65536, ftbl0TrumpetLeadSIG0);
		deleteTrumpetLeadSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(3926.9907f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / TrumpetLead_faustpower2_f(fConst1));
		float fConst3 = fConst0 * std::sin(7853.9814f / fConst0);
		float fConst4 = 2199.1147f / fConst3;
		float fConst5 = 1.0f / fConst1;
		fConst6 = (fConst5 - fConst4) / fConst1 + 1.0f;
		fConst7 = 1.0f / ((fConst5 + fConst4) / fConst1 + 1.0f);
		fConst8 = std::max<float>(1.0f, 0.008f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 0.25f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst11 = 1.0f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst12 = 3.1415927f / fConst0;
		float fConst13 = std::tan(10681.415f / fConst0);
		fConst14 = 2.0f * (1.0f - 1.0f / TrumpetLead_faustpower2_f(fConst13));
		float fConst15 = 1.0f / fConst13;
		fConst16 = (fConst15 + -0.8333333f) / fConst13 + 1.0f;
		float fConst17 = (fConst15 + 0.8333333f) / fConst13 + 1.0f;
		fConst18 = 1.0f / fConst17;
		fConst19 = 0.15f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst20 = 1.0f / (fConst13 * fConst17);
		fConst21 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst22 = 1.0f / std::max<float>(1.0f, 0.35f * fConst0);
		fConst23 = 5.5f / fConst0;
		fConst24 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst25 = 1.0f / fConst0;
		float fConst26 = 3910.6406f / fConst3;
		fConst27 = (fConst5 - fConst26) / fConst1 + 1.0f;
		fConst28 = (fConst5 + fConst26) / fConst1 + 1.0f;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.6f);
		fHslider1 = FAUSTFLOAT(0.6f);
		fHslider2 = FAUSTFLOAT(0.02f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(4.4e+02f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec5[l4] = 0;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec9[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec3[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec0[l11] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual TrumpetLead* clone() {
		return new TrumpetLead();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("trumpet_lead");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.004f), FAUSTFLOAT(0.2f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bright", &fHslider0, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider1, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("vibrato", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 4.6e+03f * float(fHslider0) + 9e+02f;
		float fSlow3 = float(fHslider1);
		float fSlow4 = 0.45f * fSlow3 + 0.55f;
		float fSlow5 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = 0.02f * float(fHslider3);
		float fSlow8 = float(fHslider4);
		float fSlow9 = 0.44f * fSlow3;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			float fTemp0 = fConst2 * fRec0[1];
			fVec1[0] = fSlow0;
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			iRec2[0] = iSlow1 * (iRec2[1] + 1);
			float fTemp1 = float(iRec2[0]);
			float fTemp2 = 1.0f - fConst11 * fTemp1;
			float fTemp3 = std::tan(fConst12 * std::min<float>(fSlow4 * (fSlow2 * std::max<float>(0.0f, fTemp2 * std::min<float>(fConst9 * fRec1[0], std::max<float>(fConst10 * (fConst8 - fRec1[0]) + 1.0f, 0.75f))) + 6.5e+02f), 1.6e+04f));
			float fTemp4 = 1.0f / fTemp3;
			float fTemp5 = (fTemp4 + 0.8695652f) / fTemp3 + 1.0f;
			float fTemp6 = std::max<float>(0.0f, std::min<float>(fSlow6 * fRec1[0], std::max<float>(fConst19 * (fSlow5 - fRec1[0]) + 1.0f, 0.85f)) * fTemp2);
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			fRec4[0] = 5.5879355e-12f * float(iRec5[0]) * fTemp6 - fConst18 * (fConst16 * fRec4[2] + fConst14 * fRec4[1]);
			float fTemp7 = ((1 - iVec0[1]) ? 0.0f : fConst23 + fRec9[1]);
			fRec9[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow8 * (0.015f * std::max<float>(0.0f, std::min<float>(fConst24 * fRec1[0], 1.0f) - fConst24 * fTemp1) + 0.985f) * (fSlow7 * ftbl0TrumpetLeadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst22 * fRec1[0], 1.0f) - fConst21 * fTemp1) + 1.0f)));
			float fTemp9 = fRec6[1] + fConst25 * fTemp8;
			float fTemp10 = fTemp9 + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			fRec6[0] = ((iTemp11) ? fTemp9 : fTemp10);
			float fRec7 = ((iTemp11) ? fTemp9 : fTemp9 + fTemp10 * (1.0f - fConst0 / fTemp8));
			fRec3[0] = fSlow9 * ((2.0f * fRec7 + -1.0f) * fTemp6 + fConst20 * (fRec4[0] - fRec4[2])) - (fRec3[2] * ((fTemp4 + -0.8695652f) / fTemp3 + 1.0f) + 2.0f * fRec3[1] * (1.0f - 1.0f / TrumpetLead_faustpower2_f(fTemp3))) / fTemp5;
			fRec0[0] = (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) / fTemp5 - fConst7 * (fConst6 * fRec0[2] + fTemp0);
			float fTemp12 = fConst7 * (fTemp0 + fConst28 * fRec0[0] + fConst27 * fRec0[2]);
			output0[i0] = FAUSTFLOAT(fTemp12);
			output1[i0] = FAUSTFLOAT(fTemp12);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			fRec1[1] = fRec1[0];
			iRec2[1] = iRec2[0];
			iRec5[1] = iRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec9[1] = fRec9[0];
			fRec6[1] = fRec6[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
